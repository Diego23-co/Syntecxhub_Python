
import argparse
import csv
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import requests
import pandas as pd


DATABASE = "news.db"

SOURCES = {
    "bbc": "https://feeds.bbci.co.uk/news/rss.xml",
    "npr": "https://feeds.npr.org/1001/rss.xml",
    "guardian": "https://www.theguardian.com/world/rss",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


def parse_date(value):
    if not value:
        return ""

    try:
        date = parsedate_to_datetime(value)
        return date.isoformat()
    except (TypeError, ValueError, OverflowError):
        return value


def fetch_feed(source, url):
    """Fetch and parse headlines from one RSS feed."""
    articles = []

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "NewsAggregatorCLI/1.0"}
        )
        response.raise_for_status()

        root = ElementTree.fromstring(response.content)

        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            published = parse_date(
                item.findtext("pubDate") or ""
            )

            if title and link:
                articles.append({
                    "source": source,
                    "title": title,
                    "url": link,
                    "published": published,
                    "fetched_at": datetime.now(
                        timezone.utc
                    ).isoformat()
                })

        logging.info(
            "Fetched %d headlines from %s",
            len(articles), source
        )

    except (
        requests.RequestException,
        ElementTree.ParseError,
        ValueError
    ) as error:
        logging.warning("Could not fetch %s: %s", source, error)

    # Be polite when requesting multiple sources.
    time.sleep(1)
    return articles


def fetch_news(selected_sources):
    articles = []

    for source in selected_sources:
        url = SOURCES.get(source.lower())

        if url:
            articles.extend(fetch_feed(source.lower(), url))
        else:
            logging.warning("Unknown source: %s", source)

    return articles


def remove_duplicates(articles):
    """Prefer matching article URLs, then matching titles."""
    unique = []
    seen_urls = set()
    seen_titles = set()

    for article in articles:
        url = article["url"].strip().rstrip("/")
        title = article["title"].strip().casefold()

        if url in seen_urls or title in seen_titles:
            continue

        seen_urls.add(url)
        seen_titles.add(title)
        unique.append(article)

    return unique


def filter_news(articles, source=None, keyword=None, date=None):
    results = articles

    if source:
        results = [
            item for item in results
            if item["source"].casefold() == source.casefold()
        ]

    if keyword:
        results = [
            item for item in results
            if keyword.casefold() in item["title"].casefold()
        ]

    if date:
        results = [
            item for item in results
            if item["published"][:10] == date
        ]

    return results


def save_json(articles, filename):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(articles, file, indent=4, ensure_ascii=False)

    logging.info("Saved JSON: %s", path)


def save_sqlite(articles, filename=DATABASE):
    with sqlite3.connect(filename) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS news (
                source TEXT,
                title TEXT,
                url TEXT UNIQUE,
                published TEXT,
                fetched_at TEXT
            )
        """)

        connection.executemany("""
            INSERT OR IGNORE INTO news
            (source, title, url, published, fetched_at)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (
                a["source"], a["title"], a["url"],
                a["published"], a["fetched_at"]
            )
            for a in articles
        ])

    logging.info("Saved articles to SQLite: %s", filename)


def export_news(articles, filename):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()

    if suffix == ".json":
        save_json(articles, path)
    elif suffix == ".csv":
        columns = [
            "source", "title", "url", "published", "fetched_at"
        ]
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(articles)
    elif suffix == ".xlsx":
        pd.DataFrame(articles).to_excel(path, index=False)
    else:
        raise ValueError("Export format must be .json, .csv, or .xlsx")

    logging.info("Exported %d articles to %s", len(articles), path)


def main():
    parser = argparse.ArgumentParser(
        description="Collect, filter, and export news headlines."
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=list(SOURCES.keys()),
        default=list(SOURCES.keys()),
        help="Sources to fetch"
    )
    parser.add_argument("--source", help="Filter by source")
    parser.add_argument("--keyword", help="Filter headlines by keyword")
    parser.add_argument("--date", help="Filter by date (YYYY-MM-DD)")
    parser.add_argument(
        "--output", default="news.json",
        help="Output file (.json, .csv, or .xlsx)"
    )
    parser.add_argument(
        "--database", default=DATABASE,
        help="SQLite database path"
    )

    args = parser.parse_args()

    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            parser.error("--date must use YYYY-MM-DD format")

    articles = fetch_news(args.sources)
    articles = remove_duplicates(articles)
    results = filter_news(
        articles,
        source=args.source,
        keyword=args.keyword,
        date=args.date
    )

    logging.info(
        "Collected %d unique headlines; %d match your filters.",
        len(articles), len(results)
    )

    try:
        save_sqlite(articles, args.database)
        export_news(results, args.output)
    except (OSError, sqlite3.Error, ValueError, ImportError) as error:
        logging.error("Could not save results: %s", error)
        sys.exit(1)

    for article in results:
        print(f"\n[{article['source']}] {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Published: {article['published'] or 'Unknown'}")


if __name__ == "__main__":
    main()
