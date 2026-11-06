import re

def parse_book_card(card_html: str, exchange_rate: float = 1.0) -> dict:
    """Parses individual book snippet and converts GBP price to USD using live rate."""
    title_match = re.search(r'title="([^"]+)"', card_html)
    price_match = re.search(r'class="price_color">\s*([^<]+)', card_html)
    rating_match = re.search(r'class="star-rating\s+(\w+)"', card_html)
    stock_match = re.search(r'class="instock availability">\s*<i class="[^"]+"></i>\s*([\w\s]+?)\s*</p>', card_html)

    raw_title = title_match.group(1) if title_match else "Unknown"
    raw_price = price_match.group(1) if price_match else "£0.00"
    raw_rating = rating_match.group(1) if rating_match else "None"
    raw_stock = stock_match.group(1) if stock_match else "Out of stock"

    # Clean non-numeric characters to extract raw GBP value
    clean_gbp_str = re.sub(r'[^\d.]', '', raw_price)
    price_gbp = float(clean_gbp_str) if clean_gbp_str else 0.0
    
    # Dynamic conversion to USD
    price_usd = round(price_gbp * exchange_rate, 2)
    clean_stock = re.sub(r'\s+', ' ', raw_stock).strip()

    return {
        "title": raw_title,
        "price_gbp": price_gbp,
        "price": price_usd,  # Output price in USD
        "rating": raw_rating,
        "in_stock": clean_stock.lower() == "in stock"
    }

def parse_page_html(html: str, exchange_rate: float = 1.0) -> list[dict]:
    """Isolates book cards via re.findall and maps parser with live rate."""
    book_cards = re.findall(r'<article class="product_pod">.*?</article>', html, flags=re.DOTALL)
    return [parse_book_card(card, exchange_rate) for card in book_cards]
