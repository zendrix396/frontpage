from celery import shared_task
from nsepython import nsefetch
from .models import Stock

@shared_task
def fetch_stock_data():
    print("Fetching stock data...")
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