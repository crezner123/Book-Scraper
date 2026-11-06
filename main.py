import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fetcher import fetch_and_parse
from analytics import compute_catalog_stats

def usage(exit_code: int = 0):
    """Prints usage instructions and exits with the specified code."""
    prog_name = sys.argv[0] if sys.argv[0] else "main.py"
    print(f"Usage: python {prog_name} [-c CORES] [-p PAGES] [-h]")
    print("\nOptions:")
    print("  -c CORES    Number of worker processes for ProcessPoolExecutor")
    print("  -p PAGES    Number of catalogue pages to scrape (default: 20)")
    print("  -h          Display this help message and exit")
    sys.exit(exit_code)

def parse_cli_args(args: list[str]) -> tuple[int | None, int]:
    """Parses command line arguments using popping while-loop queue semantics."""
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
            # Triggered for any unallowed flag
            usage(1)

    # Any unexpected positional arguments remaining
    if args:
        usage(1)

    return cores, pages

def generate_urls(page_count: int) -> list[str]:
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    return [base_url.format(i) for i in range(1, page_count + 1)]

def main():
    # Pass a copy of sys.argv[1:] so original sys.argv remains intact
    cores, pages = parse_cli_args(sys.argv[1:])
    urls = generate_urls(pages)
    
    print(f"[*] Starting scrape across {len(urls)} pages...")
    print(f"[*] Process Workers (-c): {cores or 'Auto (System CPU Count)'}")

    start_time = time.perf_counter()

    with ProcessPoolExecutor(max_workers=cores) as executor:
        page_results = list(executor.map(fetch_and_parse, urls))

    all_books = [book for page in page_results for book in page]
    
    elapsed_time = time.perf_counter() - start_time
    stats = compute_catalog_stats(all_books)

    print("\n" + "=" * 45)
    print("      SCRAPER PERFORMANCE & RESULTS")
    print("=" * 45)
    print(f"Total Pages Scraped : {pages}")
    print(f"Total Books Extracted: {stats['total_items']}")
    print(f"In-Stock Items      : {stats['in_stock_items']}")
    print(f"Average Price       : ${stats['average_in_stock_price']:.2f}")
    print("-" * 45)
    print(f"Execution Time      : {elapsed_time:.3f} seconds")
    print(f"Throughput          : {pages / elapsed_time:.2f} pages/sec")
    print("=" * 45)

if __name__ == "__main__":
    main()
