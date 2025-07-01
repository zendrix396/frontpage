from celery import shared_task
from nsepython import nsefetch
from .models import Stock
from authorization.models import StockOwnership, UserCreds
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
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

    positions = nsefetch("https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O")
    for stock in positions['data']:
        symbol = stock.get('meta',{}).get("symbol")
        if not symbol:
            continue
        stock_obj, created = Stock.objects.update_or_create(
        symbol=symbol,
        defaults={
            'name': stock.get("meta", {}).get("companyName", "N/A"),
            'dayHigh': stock.get("dayHigh", 0.0),
            'dayLow': stock.get("dayLow", 0.0),
            'lastPrice': stock.get("lastPrice", 0.0),
            'pChange': stock.get("pChange", 0.0),
        }
    )
    print(f"Updated {stock_obj.symbol}: ₹{stock_obj.lastPrice} ({stock_obj.pChange}%)")

    for user in UserCreds.objects.all():
        for stuff in user.owned_stocks.all():
            print("setting profits")
            stock = Stock.objects.get(symbol=stuff.symbol)
            stuff.profit =round((stuff.quantity*stock.lastPrice)-(stuff.quantity*stuff.brought_prize),2)
            stuff.save()
