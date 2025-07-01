from celery import shared_task
from nsepython import nsefetch
from .models import Stock
from authorization.models import StockOwnership, UserCreds
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
from collections import defaultdict

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
        user.unrealized_gain = 0
        for stuff in user.owned_stocks.all():
            print("setting profits")
            stock = Stock.objects.get(symbol=stuff.symbol)
            stuff.profit = round(stuff.quantity*(stock.lastPrice-stuff.brought_prize),2)
            user.unrealized_gain+=stuff.profit
            stuff.save()
            user.save()
    # UserCreds.objects.all().update(unrealized_gain=0)
    # for stock in Stock.objects.all():
    #     if stock in StockOwnership.objects.filter(symbol=stock.symbol):
    #         for instance in StockOwnership.objects.filter(symbol=stock.symbol):
    #             instance.profit = round((instance.quantity*stock.lastPrice)-(instance.quantity*instance.brought_prize), 2)
    #             getUser = instance.user
    #             getUser.unrealized_gain+=instance.profit
    #             instance.save()
    #             getUser.save()        
    # UserCreds.objects.all().update(unrealized_gain=0)

    # Step 1: Cache all stock prices
    # stock_prices = {
    #     stock.symbol: stock.lastPrice
    #     for stock in Stock.objects.all()
    # }

    # Step 2: Prefetch all stock ownerships and update profit in memory
    # ownerships = StockOwnership.objects.select_related('user').all()

    # # Track user gain accumulation
    # user_gains = defaultdict(float)
    # to_update_ownerships = []
    # to_update_users = {}

    # for instance in ownerships:
    #     last_price = stock_prices.get(instance.symbol)
    #     if last_price is None:
    #         continue

    #     profit = round(instance.quantity * (last_price - instance.brought_prize), 2)
    #     instance.profit = profit
    #     to_update_ownerships.append(instance)

    #     user_gains[instance.user_id] += profit

    # # Step 3: Apply profit updates in bulk
    # StockOwnership.objects.bulk_update(to_update_ownerships, ['profit'])

    # # Step 4: Apply unrealized_gain updates in bulk
    # for user_id, total_gain in user_gains.items():
    #     to_update_users[user_id] = total_gain

    # users = UserCreds.objects.filter(id__in=to_update_users.keys())
    # for user in users:
    #     user.unrealized_gain = to_update_users[user.id]
    # UserCreds.objects.bulk_update(users, ['unrealized_gain'])