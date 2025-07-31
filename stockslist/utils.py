from datetime import datetime, time
import pytz

def is_market_open():
    """
    Check if Indian stock market is currently open.
    Market hours: 9:15 AM to 3:30 PM, Monday to Friday (IST)
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    market_open = time(9, 15)  
    market_close = time(15, 30)  
    
    current_time = now.time()
    
    return market_open <= current_time <= market_close

def get_market_status():
    """
    Get market status with additional information
    """
    is_open = is_market_open()
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if is_open:
        return {
            'is_open': True,
            'message': 'Markets are open',
            'next_close': f"Closes at 3:30 PM IST"
        }
    else:
        if now.weekday() >= 5:
            return {
                'is_open': False,
                'message': 'Markets are closed (Weekend)',
                'next_open': f"Opens Monday at 9:15 AM IST"
            }
        else:
            if now.time() < time(9, 15):
                return {
                    'is_open': False,
                    'message': 'Markets are closed',
                    'next_open': f"Opens today at 9:15 AM IST"
                }
            else:
                return {
                    'is_open': False,
                    'message': 'Markets are closed',
                    'next_open': f"Opens tomorrow at 9:15 AM IST"
                } 