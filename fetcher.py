import warnings
warnings.filterwarnings("ignore")

import requests
from parser import parse_page_html

def fetch_and_parse(url: str, exchange_rate: float = 1.0) -> list[dict]:
    """Pickleable target function for ProcessPoolExecutor."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return parse_page_html(response.text, exchange_rate)
