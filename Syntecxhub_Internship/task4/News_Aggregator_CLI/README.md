# News Aggregator CLI

A Python command-line application that collects news headlines from multiple RSS feeds, removes duplicates, filters results, and stores articles in SQLite.

## Features

- Fetches headlines from BBC, NPR, and The Guardian RSS feeds
- Filters by source, keyword, and publication date
- Removes duplicate articles
- Saves collected articles in SQLite
- Exports filtered results to JSON, CSV, or Excel
- Includes logging, timeouts, and error handling

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

Fetch headlines from all sources and export to JSON:

```bash
python news_aggregator.py --output news.json
```

Filter by keyword:

```bash
python news_aggregator.py --keyword technology --output technology.csv
```

Choose sources:

```bash
python news_aggregator.py --sources bbc guardian --output news.xlsx
```

Filter by source and date:

```bash
python news_aggregator.py --source bbc --date 2026-10-24 --output filtered.json
```

## Requirements

Python 3.10 or newer, an internet connection, and the dependencies listed in `requirements.txt`.
