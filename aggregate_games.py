import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path
from dateutil import parser as date_parser

GAME_FILES = [
    "africa_cup_games.json",
    "copa_america_games.json",
    "euro_games.json",
    "friendlies_games.json",
    "gold_cup_games.json",
    "oceania_cup_games.json",
    "world_cup_games.json",
]


def parse_game_date(date_str):
    if not date_str:
        return None

    try:
        dt = date_parser.parse(date_str, dayfirst=True, fuzzy=True)
        return dt.date().isoformat()
    except Exception:
        return None


def parse_score(result):
    if not isinstance(result, str):
        return None, None

    match = re.search(r"(\d+)\s*[:\-]\s*(\d+)", result)
    if not match:
        return None, None

    return int(match.group(1)), int(match.group(2))


def normalize_text(value):
    if value is None:
        return None

    text = str(value).strip().casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text)


def clean_team_name(name):
    if name is None:
        return None

    # Remove sufixos comuns como U20, U21, etc.
    name = re.sub(r'\s+U\d+', '', str(name).strip())
    # Remove outros sufixos se necessário, ex: (A), (B), etc.
    name = re.sub(r'\s+\([A-Z]\)', '', name)
    return name


def parse_match_score(score):
    if score is None:
        return None, None

    if isinstance(score, (int, float)):
        score = str(score)

    return parse_score(str(score))


def build_match_key(date_value, home_team, away_team, home_score, away_score):
    return (
        normalize_text(date_value),
        normalize_text(clean_team_name(home_team)),
        normalize_text(clean_team_name(away_team)),
        f"{home_score}:{away_score}" if home_score is not None and away_score is not None else None,
    )


def load_match_file(path: Path):
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            home_score, away_score = parse_match_score(row.get("score"))
            rows.append(
                {
                    "date": row.get("date"),
                    "date_iso": parse_game_date(row.get("date")),
                    "home_team": row.get("home_team"),
                    "away_team": row.get("away_team"),
                    "home_score": home_score,
                    "away_score": away_score,
                    "match_key": build_match_key(
                        row.get("date"),
                        row.get("home_team"),
                        row.get("away_team"),
                        home_score,
                        away_score,
                    ),
                }
            )
    return rows


def count_matching_games(aggregated_df, matches_path: Path):
    if matches_path is None or not matches_path.exists():
        return 0, len(aggregated_df), 0

    match_rows = load_match_file(matches_path)
    match_keys = {row["match_key"] for row in match_rows if row["match_key"] is not None}
    aggregated_keys = []
    for _, row in aggregated_df.iterrows():
        aggregated_keys.append(
            build_match_key(
                row.get("game_date_iso") or row.get("date"),
                row.get("home_club_name"),
                row.get("away_club_name"),
                row.get("home_score"),
                row.get("away_score"),
            )
        )

    matched = [key for key in aggregated_keys if key in match_keys]
    return len(matched), len(aggregated_keys), len(match_rows)


def extract_player_name_from_href(href):
    if not isinstance(href, str):
        return None

    slug = href.strip("/")
    if not slug:
        return None

    slug = slug.split("/")[0]
    return slug.replace("-", " ").title()


def collect_players(record):
    players = {}
    for event in record.get("events") or []:
        club_name = event.get("club", {}).get("name")
        event_type = event.get("type")
        minute = event.get("minute")

        for role in ("player", "player_in", "player_assist"):
            player_obj = event.get(role)
            if not isinstance(player_obj, dict):
                continue

            href = player_obj.get("href")
            if not href:
                continue

            if href not in players:
                players[href] = {
                    "href": href,
                    "name": extract_player_name_from_href(href),
                    "team": club_name,
                    "roles": set(),
                    "event_types": set(),
                    "minutes": [],
                }

            players[href]["roles"].add(role)
            if event_type:
                players[href]["event_types"].add(event_type)
            if minute is not None:
                players[href]["minutes"].append(minute)
            if not players[href]["team"] and club_name:
                players[href]["team"] = club_name

    normalized = []
    for player in players.values():
        normalized.append(
            {
                "href": player["href"],
                "name": player["name"],
                "team": player["team"],
                "roles": sorted(player["roles"]),
                "event_types": sorted(player["event_types"]),
                "minutes": sorted(set(player["minutes"])),
            }
        )

    return normalized


def parse_json_file(path: Path):
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        items = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
        return items

    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported JSON structure in {path}")


def flatten_game(record: dict, source_file: str) -> dict:
    parent = record.get("parent", {}) or {}
    game_date_iso = parse_game_date(record.get("date"))
    home_score, away_score = parse_score(record.get("result"))
    players = collect_players(record)
    home_players = [p["name"] for p in players if p.get("team") == record.get("home_club_name")]
    away_players = [p["name"] for p in players if p.get("team") == record.get("away_club_name")]

    return {
        "source_file": source_file,
        "competition_name": parent.get("competition_name"),
        "competition_type": parent.get("competition_type"),
        "competition_href": parent.get("href"),
        "seasoned_href": parent.get("seasoned_href"),
        "game_id": record.get("game_id"),
        "game_href": record.get("href"),
        "home_club_name": record.get("home_club_name"),
        "home_club_href": record.get("home_club", {}).get("href"),
        "away_club_name": record.get("away_club_name"),
        "away_club_href": record.get("away_club", {}).get("href"),
        "date": record.get("date"),
        "game_date_iso": game_date_iso,
        "kickoff_time": record.get("kickoff_time"),
        "matchday": record.get("matchday"),
        "result": record.get("result"),
        "home_score": home_score,
        "away_score": away_score,
        "half_time_score": record.get("half_time_score"),
        "stadium": record.get("stadium"),
        "attendance": record.get("attendance"),
        "referee": record.get("referee"),
        "referee_href": record.get("referee_href"),
        "events": record.get("events"),
        "players_involved": players,
        "home_players_involved": home_players,
        "away_players_involved": away_players,
        "home_manager": record.get("home_manager"),
        "away_manager": record.get("away_manager"),
    }


def load_all_games(directory: Path):
    games = []
    for filename in GAME_FILES:
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        items = parse_json_file(path)
        for item in items:
            games.append(flatten_game(item, filename))

    return games


def main():
    parser = argparse.ArgumentParser(
        description="Carrega vários arquivos JSON de jogos e cria um DataFrame agregado."
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("."),
        help="Diretório onde estão os arquivos JSON de jogos.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Salva o DataFrame agregado em CSV ou JSON. Use extensão .csv ou .json.",
    )
    parser.add_argument(
        "--match-file",
        type=Path,
        default=None,
        help="Arquivo matches.csv para comparar os jogos agregados.",
    )
    args = parser.parse_args()

    games = load_all_games(args.dir)

    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "Para executar este script, instale pandas: pip install pandas"
        )

    df = pd.DataFrame(games)

    if args.output:
        output = args.output
        if output.suffix.lower() == ".csv":
            df.to_csv(output, index=False)
        elif output.suffix.lower() == ".json":
            df.to_json(output, orient="records", force_ascii=False, indent=2)
        else:
            raise ValueError("O arquivo de saída deve terminar em .csv ou .json")
        print(f"Dados agregados salvos em: {output}")
    else:
        df.to_csv("all_games.csv", index=False)
        print(df)
        print(df.info())
        print("\nContagem de jogos por competição:\n")
        print(df["competition_name"].value_counts())

    match_file = args.match_file or (args.dir / "matches.csv")
    if match_file.exists():
        matched_count, all_games_count, matches_count = count_matching_games(df, match_file)
        print(f"\nComparação com {match_file}:")
        print(f"  - total all_games: {all_games_count}")
        print(f"  - total matches: {matches_count}")
        print(f"  - jogos que coincidem com chave composta (data, times e placar): {matched_count}")
    elif args.match_file:
        print(f"Arquivo de comparação não encontrado: {match_file}")

#==========================================================

if __name__ == "__main__":
    main()
