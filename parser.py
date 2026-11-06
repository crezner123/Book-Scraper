import re

def parse_book_card(card_html: str) -> dict:
    """Parses an individual book HTML snippet using re.search and re.sub."""
    title_match = re.search(r'title="([^"]+)"', card_html)
    price_match = re.search(r'class="price_color">\s*([^<]+)', card_html)
    rating_match = re.search(r'class="star-rating\s+(\w+)"', card_html)
    stock_match = re.search(r'class="instock availability">\s*<i class="[^"]+"></i>\s*([\w\s]+?)\s*</p>', card_html)

    raw_title = title_match.group(1) if title_match else "Unknown"
    raw_price = price_match.group(1) if price_match else "$0.00"
    raw_rating = rating_match.group(1) if rating_match else "None"
    raw_stock = stock_match.group(1) if stock_match else "Out of stock"

    clean_price_str = re.sub(r'[^\d.]', '', raw_price)
    clean_stock = re.sub(r'\s+', ' ', raw_stock).strip()

    return {
        "title": raw_title,
        "price": float(clean_price_str) if clean_price_str else 0.0,
        "rating": raw_rating,
        "in_stock": clean_stock.lower() == "in stock"
    }

def parse_page_html(html: str) -> list[dict]:
    """Extracts book product blocks using re.findall and maps parsing."""
    book_cards = re.findall(r'<article class="product_pod">.*?</article>', html, flags=re.DOTALL)
    return list(map(parse_book_card, book_cards))
