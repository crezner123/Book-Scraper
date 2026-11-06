import requests
from parser import parse_page_html

def fetch_and_parse(url: str) -> list[dict]:
    """Pickleable target function for ProcessPoolExecutor worker tasks."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return parse_page_html(response.text)
