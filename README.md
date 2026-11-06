# Book Scraper

## Overview

This project is a high-performance web scraper built in Python to collect catalogue data from `books.toscrape.com`. It extracts book details—including titles, availability, star ratings, and prices—across multiple pages. The scraper incorporates dynamic currency conversion, fetching real-time exchange rates to convert prices from British Pounds (GBP) to US Dollars (USD) on the fly. 

To achieve maximum throughput, the application uses Python's `concurrent.futures.ProcessPoolExecutor` alongside functional programming paradigms, enabling efficient parallel processing across multiple CPU cores.

## How to Use

### Prerequisites
Ensure Python 3.8+ and `requests` are installed on your machine:

```bash
pip install requests
chmod +x main.py
```

### Execution & CLI Options

Run the script from your terminal using standard options or manual CLI flags:

```bash
# View usage instructions and available flags
./main.py -h

# Run default scrape (20 pages, auto-detect CPU cores)
./main.py

# Run single-worker baseline (1 process)
./main.py -c 1

# Run with 4 worker processes across 20 pages
./main.py -c 4

# Run with 8 worker processes across 30 catalogue pages
./main.py -p 30 -c 8
```

## Screenshot

<img width="568" height="285" alt="image" src="https://github.com/user-attachments/assets/192cd23f-5c15-4351-979b-78341f6e5f1e" />

## Performance Benchmarks

The following benchmarks demonstrate scraper performance across 20 catalogue pages (400 total books extracted) on a multi-core system:

| Worker Processes (`-c`) | Execution Time (Seconds) | Throughput (Pages/Sec) | Relative Speedup |
| :--- | :--- | :--- | :--- |
| **1 Worker** | 3.256 s | 6.14 pages/sec | 1.00x (Baseline) |
| **4 Workers** | 0.938 s | 21.32 pages/sec | 3.47x |
| **8 Workers** | 0.627 s | 31.90 pages/sec | 5.19x |
| **16 Workers** | 0.531 s | 37.68 pages/sec | 6.13x |
| **Auto (System Cores)** | 0.465 s | 43.05 pages/sec | 7.00x |

## Performance Impact & Architecture

### concurrent.futures
Multi-processing via `concurrent.futures.ProcessPoolExecutor` allows the scraper to execute tasks in parallel across separate CPU cores. The scraping task involves fetching HTML pages over HTTP, isolating book cards via regular expressions (`re.findall`), parsing metadata fields (`re.search`), cleaning raw price strings (`re.sub`), and calculating currency conversions.

By distributing page URLs across multiple worker processes with `executor.map()`, network wait times overlap and HTML string parsing executes concurrently. This reduces total execution time from **3.256 seconds** (1 worker) to **0.465 seconds** (auto/multi-worker)—a **7.00x speedup**. 

As worker counts increase beyond core capacity, speedup gains flatten out. This scaling limit is governed by network latency bottlenecks from the target web server and the cost of communication between the main process and worker functions when passing parameters and aggregating results.

### Functional Programming
The scraper's architecture relies on pure, side-effect-free functions (`fetch_and_parse`, `parse_page_html`, and `parse_book_card`). Each function operates exclusively on explicitly passed arguments—such as the target page URL and the live exchange rate multiplier—and returns fresh data dictionaries without mutating external state.

By eliminating shared state and side effects, worker functions can run independently across isolated worker processes. Additionally, `functools.partial` is used to pre-bind the live exchange rate to the worker function, enabling clean functional mapping over URL iterables via `executor.map()` without global variables.
