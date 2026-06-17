"""
LinkedIn scraper using Apify API.

Supports scraping:
  - Person profiles        (--type person)
  - Company profiles       (--type company)
  - Posts / activity       (--type posts)
  - Search results         (--type search)

Usage:
  python scraper.py --type person --urls https://www.linkedin.com/in/someone/
  python scraper.py --type company --file urls.txt --output results.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

# Apify actor IDs for each scrape type
ACTORS = {
    "person": "2SyF0bVxmgGr8IVCZ",   # LinkedIn Profile Scraper
    "company": "l1NZEFv4JM0glzMdw",   # LinkedIn Company Scraper
    "posts": "fetchfy~linkedin-post-scraper",  # LinkedIn Post Scraper
    "search": "curious_coder~linkedin-search-scraper",  # LinkedIn Search Scraper
}

# Input schema per actor type
def build_input(scrape_type: str, urls: list[str]) -> dict:
    if scrape_type == "person":
        return {"profileUrls": urls}
    elif scrape_type == "company":
        return {"startUrls": [{"url": u} for u in urls]}
    elif scrape_type == "posts":
        return {"profileUrls": urls, "maxPosts": 50}
    elif scrape_type == "search":
        return {"startUrls": [{"url": u} for u in urls], "maxResults": 100}
    raise ValueError(f"Unknown scrape type: {scrape_type}")


def run_scraper(scrape_type: str, urls: list[str], output_path: str | None) -> list[dict]:
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        sys.exit("Error: APIFY_API_TOKEN not set. Copy .env.example to .env and fill in your token.")

    client = ApifyClient(token)
    actor_id = ACTORS[scrape_type]
    actor_input = build_input(scrape_type, urls)

    print(f"Starting Apify actor '{actor_id}' for {len(urls)} URL(s)...")
    run = client.actor(actor_id).call(run_input=actor_input)

    print(f"Run finished. Fetching results from dataset '{run['defaultDatasetId']}'...")
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"Got {len(items)} item(s).")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"Results saved to: {output_path}")
    else:
        print(json.dumps(items, ensure_ascii=False, indent=2))

    return items


def load_urls(args_urls: list[str], file_path: str | None) -> list[str]:
    urls = list(args_urls or [])
    if file_path:
        with open(file_path, encoding="utf-8") as f:
            urls += [line.strip() for line in f if line.strip()]
    if not urls:
        sys.exit("Error: provide at least one URL via --urls or --file.")
    return urls


def main():
    parser = argparse.ArgumentParser(description="LinkedIn scraper via Apify API")
    parser.add_argument(
        "--type",
        required=True,
        choices=ACTORS.keys(),
        help="Type of data to scrape",
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        default=[],
        metavar="URL",
        help="One or more LinkedIn URLs",
    )
    parser.add_argument(
        "--file",
        metavar="FILE",
        help="Path to a text file with one URL per line",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Save results to this JSON file (default: print to stdout)",
    )

    args = parser.parse_args()
    urls = load_urls(args.urls, args.file)
    run_scraper(args.type, urls, args.output)


if __name__ == "__main__":
    main()
