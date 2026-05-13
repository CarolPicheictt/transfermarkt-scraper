# Tutorial Completo: Transfermarkt Scraper

## Introdução

Este projeto é um scraper para o site Transfermarkt, que coleta dados de jogos de competições internacionais de futebol. Ele permite extrair informações detalhadas sobre jogos, incluindo datas, placares, jogadores envolvidos, eventos e muito mais.

O scraper é escrito em Python e usa bibliotecas como `requests`, `beautifulsoup4` e `pandas` para coleta e processamento de dados.

## Pré-requisitos

- **Python 3.8+**: Certifique-se de ter o Python instalado. Você pode baixar em [python.org](https://www.python.org/).
- **Poetry** (opcional, mas recomendado): Para gerenciamento de dependências. Instale com `pip install poetry`.
- **Dependências**: O projeto usa as seguintes bibliotecas principais:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `dateutil`
  - `lxml` (para parsing HTML)

## Instalação

1. **Clone ou baixe o repositório**:
   ```
   git clone https://github.com/seu-usuario/transfermarkt-scraper.git
   cd transfermarkt-scraper
   ```

2. **Instale as dependências**:
   - Com Poetry (recomendado):
     ```
     poetry install
     ```
   - Ou com pip:
     ```
     pip install -r requirements.txt
     ```
     (Se não houver requirements.txt, instale manualmente: `pip install requests beautifulsoup4 pandas dateutil lxml`)

3. **Verifique a instalação**:
   ```
   python -c "import requests, bs4, pandas; print('Dependências OK')"
   ```

## Como Usar o Scraper

### 1. Executar o Scraper Principal

O scraper principal é executado via `tfmkt/__main__.py` ou `python -m tfmkt`.

#### Comandos Básicos

- **Scrapear uma competição específica**:
  ```
  python -m tfmkt competitions scrape --competition africa_cup_of_nations --season 2023
  ```

- **Listar competições disponíveis**:
  ```
  python -m tfmkt competitions list
  ```

- **Scrapear jogos de uma competição**:
  ```
  python -m tfmkt games scrape --competition africa_cup_of_nations --season 2023
  ```

#### Filtros e Opções Avançadas

O scraper suporta vários filtros para personalizar a coleta de dados:

- **Por temporada (season)**: Especifique o ano da temporada.
  ```
  --season 2023
  ```

- **Por competição**: Use o tipo de competição (ex: `africa_cup_of_nations`, `copa_america`, `world_cup`).
  ```
  --competition world_cup
  ```

- **Por país**: Filtre por seleções nacionais.
  ```
  --country brazil
  ```

- **Por clube**: Para competições de clubes.
  ```
  --club "Manchester United"
  ```

- **Por data**: Filtre jogos por intervalo de datas.
  ```
  --start-date 2023-01-01 --end-date 2023-12-31
  ```

- **Limite de resultados**: Para evitar sobrecarga.
  ```
  --limit 100
  ```

- **Saída**: Especifique onde salvar os dados.
  ```
  --output data/games.json
  ```

#### Exemplos Práticos

- **Scrapear Copa América 2024**:
  ```
  python -m tfmkt games scrape --competition copa_america --season 2024 --output copa_america_2024.json
  ```

- **Scrapear jogos da Premier League 2023**:
  ```
  python -m tfmkt games scrape --competition premier_league --season 2023 --country england
  ```

- **Buscar jogos com filtros de data**:
  ```
  python -m tfmkt games scrape --competition world_cup --start-date 2022-11-20 --end-date 2022-12-18
  ```

#### Exemplo Avançado: Scrapear Múltiplas Competições com Filtros de Tempo

Para obter todas as informações disponíveis (jogos, competições, jogadores, etc.) de uma lista específica de competições em um intervalo de tempo definido, siga estes passos:

1. **Liste as competições disponíveis** para escolher as desejadas:
   ```
   python -m tfmkt competitions list
   ```

2. **Defina a lista de competições** (ex: Copa América, Africa Cup, UEFA Euro) e o período (ex: 2023-01-01 a 2023-12-31).

3. **Execute o scraper para cada competição** com filtros de data:
   ```
   # Scrapear Copa América 2023
   python -m tfmkt games scrape --competition copa_america --season 2023 --start-date 2023-01-01 --end-date 2023-12-31 --output copa_america_2023.json

   # Scrapear Africa Cup of Nations 2023
   python -m tfmkt games scrape --competition africa_cup_of_nations --season 2023 --start-date 2023-01-01 --end-date 2023-12-31 --output africa_cup_2023.json

   # Scrapear UEFA Euro 2023 (se disponível)
   python -m tfmkt games scrape --competition uefa_euro --season 2023 --start-date 2023-01-01 --end-date 2023-12-31 --output uefa_euro_2023.json
   ```

4. **Para obter dados de competições (não apenas jogos)**:
   ```
   python -m tfmkt competitions scrape --competition copa_america --season 2023 --output competitions.json
   ```

5. **Agregue todos os dados coletados** em um único arquivo usando `aggregate_games.py`:
   ```
   python aggregate_games.py --dir ./data --output all_competitions_2023.csv
   ```

Este processo coleta todas as tabelas de dados disponíveis (jogos com eventos, jogadores, placares, datas, etc.) para as competições especificadas no intervalo de tempo. Se precisar automatizar para múltiplas competições, considere criar um script bash ou Python para loopar os comandos.

### 2. Agregar Dados com aggregate_games.py

Após scrapear os dados, use o script `aggregate_games.py` para combinar múltiplos arquivos JSON em um único DataFrame e exportar para CSV ou JSON.

#### Como Executar

- **Agregação básica** (salva em `all_games.csv` automaticamente):
  ```
  python aggregate_games.py
  ```

- **Especificar diretório e saída**:
  ```
  python aggregate_games.py --dir ./data --output aggregated_games.csv
  ```

- **Comparar com arquivo de matches**:
  ```
  python aggregate_games.py --match-file matches.csv
  ```

#### Filtros e Opções

- **Diretório dos arquivos JSON**: `--dir` (padrão: `.`)
- **Arquivo de saída**: `--output` (suporta `.csv` ou `.json`)
- **Arquivo de matches para comparação**: `--match-file` (padrão: `matches.csv` no diretório)

#### Saída

O script gera um CSV com colunas como:
- `source_file`: Arquivo JSON de origem
- `competition_name`: Nome da competição
- `home_club_name`, `away_club_name`: Times
- `game_date_iso`: Data em formato ISO
- `home_score`, `away_score`: Placar
- `players_involved`: Lista de jogadores envolvidos
- E muito mais.

Além disso, compara com `matches.csv` e conta jogos coincidentes usando chave composta (data, times, placar).

### 3. Aplicar Filtros para Buscar Novos Dados

Para buscar novos dados, você pode modificar os filtros no código ou via linha de comando.

#### Modificar Filtros no Código

1. **Editar `tfmkt/crawlers/games.py`**:
   - Adicione novos filtros em `scrape_games()`.
   - Exemplo: Adicionar filtro por estádio:
     ```python
     if stadium_filter and game.get('stadium') != stadium_filter:
         continue
     ```

2. **Atualizar argumentos no CLI** (`tfmkt/cli.py`):
   - Adicione novos argumentos com `add_argument()`.

#### Exemplos de Filtros Personalizados

- **Filtrar por jogadores específicos**:
  ```
  python -m tfmkt games scrape --competition world_cup --player "Lionel Messi"
  ```

- **Filtrar por placar mínimo**:
  ```
  python -m tfmkt games scrape --competition premier_league --min-score 3
  ```

- **Buscar apenas jogos com cartões vermelhos**:
  ```
  python -m tfmkt games scrape --competition copa_america --has-red-card true
  ```

### 4. Estrutura dos Dados

#### Arquivos JSON de Saída

Cada arquivo JSON contém uma lista de dicionários com dados de jogos. Exemplo:

```json
{
  "game_id": "4225471",
  "home_club_name": "Ivory Coast",
  "away_club_name": "Nigeria",
  "date": "Thu, 18/01/24",
  "result": "0:1",
  "events": [...],
  "players_involved": [...]
}
```

#### Arquivo CSV Agregado

O `all_games.csv` agrega todos os jogos em um formato tabular, ideal para análise com pandas ou Excel.

### 5. Troubleshooting

- **Erro de dependências**: Execute `pip install -r requirements.txt` ou `poetry install`.
- **Bloqueio do site**: Transfermarkt pode bloquear IPs. Use proxies ou aguarde entre requests.
- **Dados incompletos**: Verifique se a competição/temporada existe no site.
- **Encoding issues**: Use `utf-8-sig` para arquivos CSV com BOM.
- **Performance**: Para grandes volumes, use `--limit` para testar primeiro.

### 6. Extensões e Melhorias

- **Adicionar novas competições**: Edite `tfmkt/common.py` para incluir novos tipos.
- **Integração com bancos de dados**: Modifique `aggregate_games.py` para salvar em SQL.
- **Visualização**: Use pandas e matplotlib para gráficos dos dados agregados.

### Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades. Abra issues ou pull requests no repositório.

---

Este tutorial cobre o uso básico e avançado do scraper. Para dúvidas específicas, consulte o código-fonte ou abra uma issue.</content>
<parameter name="filePath">c:\Users\Carolina\Desktop\scrapPythonFIFA\scrap\transfermarkt-scraper\TUTORIAL.md