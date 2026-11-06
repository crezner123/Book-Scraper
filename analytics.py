def compute_catalog_stats(books: list[dict]) -> dict:
    """Aggregates dataset using pure map, filter, and sum (no reduce)."""
    in_stock_books = list(filter(lambda b: b["in_stock"], books))
    prices = list(map(lambda b: b["price"], in_stock_books))
    
    total_count = len(books)
    in_stock_count = len(in_stock_books)
    avg_price = (sum(prices) / in_stock_count) if in_stock_count else 0.0

    return {
        "total_items": total_count,
        "in_stock_items": in_stock_count,
        "average_in_stock_price": round(avg_price, 2)
    }
