#!/usr/bin/env python3
import os
os.environ["PYTHONWARNINGS"] = "ignore"

import warnings
warnings.filterwarnings("ignore")

import sys
import time
from functools import partial
from concurrent.futures import ProcessPoolExecutor
import requests
from fetcher import fetch_and_parse
from analytics import compute_catalog_stats
from typing import Optional

def get_live_gbp_to_usd_rate() -> float:
    """Fetches real-time GBP to USD exchange rate from API with fallback."""
    try:
        url = "https://open.er-api.com/v6/latest/GBP"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        rate = response.json()["rates"]["USD"]
        print(f"[*] Live exchange rate fetched: 1 GBP = ${rate:.4f} USD")
        return rate
    except Exception as e:
        print(f"[!] Warning: Could not fetch live rate ({e}). Using fallback 1.27.")
        return 1.27

def usage(exit_code: int = 0):
    prog_name = sys.argv[0] if sys.argv[0] else "main.py"
    print(f"Usage: python {prog_name} [-c CORES] [-p PAGES] [-h]")
    print("\nOptions:")
    print("  -c CORES    Number of worker processes for ProcessPoolExecutor")
    print("  -p PAGES    Number of catalogue pages to scrape (default: 20)")
    print("  -h          Display this help message and exit")
    sys.exit(exit_code)

def parse_cli_args(args: list[str]) -> tuple[Optional[int], int]:
    cores = None
    pages = 20

    while args and args[0].startswith('-'):
        flag = args.pop(0)
        
        if flag == '-h':
            usage(0)
        elif flag == '-c':
            if not args:
                usage(1)
            try:
                cores = int(args.pop(0))
                if cores <= 0:
                    usage(1)
            except ValueError:
                usage(1)
        elif flag == '-p':
            if not args:
                usage(1)
            try:
                pages = int(args.pop(0))
                if pages <= 0:
                    usage(1)
            except ValueError:
                usage(1)
        else:
            usage(1)

    if args:
        usage(1)

    return cores, pages

def generate_urls(page_count: int) -> list[str]:
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    return [base_url.format(i) for i in range(1, page_count + 1)]

def main():
    cores, pages = parse_cli_args(sys.argv[1:])
    urls = generate_urls(pages)

    # 1. Fetch live GBP -> USD exchange rate once
    exchange_rate = get_live_gbp_to_usd_rate()
    
    print(f"[*] Starting scrape across {len(urls)} pages...")
    print(f"[*] Process Workers (-c): {cores or 'Auto (System CPU Count)'}")

    # 2. Partially bind exchange_rate to fetch_and_parse function
    worker_fn = partial(fetch_and_parse, exchange_rate=exchange_rate)

    start_time = time.perf_counter()

    with ProcessPoolExecutor(max_workers=cores) as executor:
        page_results = list(executor.map(worker_fn, urls))

    all_books = [book for page in page_results for book in page]
    
    elapsed_time = time.perf_counter() - start_time
    stats = compute_catalog_stats(all_books)

    print("\n" + "=" * 45)
    print("      SCRAPER PERFORMANCE & RESULTS")
    print("=" * 45)
    print(f"Total Pages Scraped : {pages}")
    print(f"Total Books Extracted: {stats['total_items']}")
    print(f"In-Stock Items      : {stats['in_stock_items']}")
    print(f"Average Price (USD) : ${stats['average_in_stock_price']:.2f}")
    print("-" * 45)
    print(f"Execution Time      : {elapsed_time:.3f} seconds")
    print(f"Throughput          : {pages / elapsed_time:.2f} pages/sec")
    print("=" * 45)

if __name__ == "__main__":
    main()
