from celery import shared_task
from nsepython import nsefetch
from .models import Stock
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import random
@shared_task
def fetch_stock_data():
    print("Fetching stock data...")
    # for stock in Stock.objects.all():
    #     if not stock.base_price:
    #         # Start with current price if base not set
    #         stock.base_price = float(stock.lastPrice or np.random.uniform(800, 2500))

    #     # Simulate a small normal fluctuation around 0 with very low std dev (e.g., ±0.15%)
    #     pct_change = np.random.normal(loc=0.0, scale=0.0015)  # = ±0.15%
    #     new_price = round(stock.base_price * (1 + pct_change), 2)

    #     # Track high/low during this "simulated day"
    #     stock.dayHigh = max(stock.dayHigh or new_price, new_price)
    #     stock.dayLow = min(stock.dayLow or new_price, new_price)

    #     # Update current price and percentage change
    #     stock.lastPrice = new_price
    #     stock.pChange = round((new_price - stock.base_price) / stock.base_price * 100, 2)

    #     stock.save()

    #     print(f"Updated {stock.symbol}: ₹{stock.lastPrice} ({stock.pChange}%)")


    positions = nsefetch("https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O")
    for stock in positions['data']:
        symbol = stock.get('meta',{}).get("symbol")
        if not symbol:
            continue
        Stock.objects.update_or_create(
            symbol=symbol,
            defaults= {
                'name': stock.get("meta", {}).get("companyName", "N/A"),
                    'dayHigh': stock.get("dayHigh", "N/A"),
                    'dayLow': stock.get("dayLow", "N/A"),
                    'lastPrice': stock.get("lastPrice", "N/A"),
                    'pChange': stock.get("pChange", "N/A"),
            }
        )
