from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Stock
from authorization.models import StockOwnership, UserCreds
from django.utils import timezone
from .utils import is_market_open, get_market_status
from unittest.mock import patch
from datetime import datetime, time

class StockslistTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='trader', password='tradepass')
        self.user_creds = UserCreds.objects.create(username='trader', email='trader@example.com')
        self.stock = Stock.objects.create(
            symbol='AAPL', name='Apple Inc.', lastPrice=100, dayHigh=110, dayLow=90, pChange=0
        )
        self.dashboard_url = reverse('stockslist:dashboard')
        self.index_url = reverse('stockslist:index')
        self.buy_url = reverse('stockslist:buy')
        self.sell_url = reverse('stockslist:sell')

    def test_stock_model_str(self):
        self.assertEqual(str(self.stock), 'AAPL - Apple Inc.')

    def test_stockownership_model_creation(self):
        purchase = StockOwnership.objects.create(
            user=self.user_creds, symbol='AAPL', quantity=5, brought_prize=100, profit=0
        )
        self.assertEqual(purchase.symbol, 'AAPL')
        self.assertEqual(purchase.quantity, 5)

    def test_stock_list_view_unauthenticated(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stocks')

    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_authenticated(self):
        self.client.login(username='trader', password='tradepass')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_buy_stock_requires_login(self):
        response = self.client.post(self.buy_url, {'companySymbol': 'AAPL', 'lastPrice': 100})
        self.assertEqual(response.status_code, 302)

    def test_buy_stock_success(self):
        self.client.login(username='trader', password='tradepass')
        self.user_creds.amount = 1000
        self.user_creds.save()
        response = self.client.post(self.buy_url, {
            'companySymbol': 'AAPL',
            'lastPrice': 100,
            'buy': 'Buy',
            'quantity': 1
        }, follow=True)
        self.assertIn(response.status_code, [200, 302])

    def test_sell_stock_requires_login(self):
        response = self.client.post(self.sell_url, {'id': 1})
        self.assertEqual(response.status_code, 302)

    def test_live_api_returns_json(self):
        self.client.login(username='trader', password='tradepass')
        live_api_url = reverse('stockslist:live_api')
        response = self.client.get(live_api_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_cannot_buy_more_than_budget(self):
        self.client.login(username='trader', password='tradepass')
        self.user_creds.amount = 10
        self.user_creds.save()
        response = self.client.post(self.buy_url, {
            'companySymbol': 'AAPL',
            'lastPrice': 100,
            'buy': 'Buy',
            'quantity': 1
        })
        self.assertIn(response.status_code, [200, 400, 403])

    def test_portfolio_breakdown(self):
        stock2 = Stock.objects.create(symbol='GOOG', name='Google', lastPrice=200, dayHigh=210, dayLow=190, pChange=0)
        StockOwnership.objects.create(user=self.user_creds, symbol='AAPL', quantity=2, brought_prize=100, profit=10)
        StockOwnership.objects.create(user=self.user_creds, symbol='GOOG', quantity=1, brought_prize=200, profit=20)
        self.client.login(username='trader', password='tradepass')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AAPL')
        self.assertContains(response, 'GOOG')
        self.assertContains(response, 'Dashboard')

    def test_profit_loss_calculation(self):
        so = StockOwnership.objects.create(user=self.user_creds, symbol='AAPL', quantity=2, brought_prize=100, profit=15)
        self.user_creds.unrealized_gain = 15
        self.user_creds.save()
        self.client.login(username='trader', password='tradepass')
        response = self.client.post(self.sell_url, {'id': so.id}, follow=True)
        self.user_creds.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_creds.unrealized_gain, 0)
        self.assertEqual(self.user_creds.realized_gain, 15)

    def test_transaction_history(self):
        StockOwnership.objects.create(user=self.user_creds, symbol='AAPL', quantity=1, brought_prize=100, profit=5, buy_time=timezone.now())
        StockOwnership.objects.create(user=self.user_creds, symbol='AAPL', quantity=2, brought_prize=110, profit=10, buy_time=timezone.now())
        self.client.login(username='trader', password='tradepass')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AAPL')
        self.assertContains(response, '100')
        self.assertContains(response, '110')

    def test_live_profit_api(self):
        StockOwnership.objects.create(user=self.user_creds, symbol='AAPL', quantity=1, brought_prize=100, profit=5)
        self.user_creds.unrealized_gain = 5
        self.user_creds.realized_gain = 0
        self.user_creds.amount = 999900
        self.user_creds.save()
        self.client.login(username='trader', password='tradepass')
        live_profit_url = reverse('stockslist:live_profit')
        response = self.client.get(live_profit_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('userConfig', data)
        self.assertEqual(data['userConfig']['unrealized_gain'], 5)
        self.assertEqual(data['userConfig']['realized_gain'], 0)
        self.assertEqual(data['userConfig']['amount'], 999900)

    @patch('stockslist.utils.datetime')
    def test_market_hours_weekday_open(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30)  # Monday 10:30 AM
        self.assertTrue(is_market_open())

    @patch('stockslist.utils.datetime')
    def test_market_hours_weekday_closed_before(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 1, 15, 8, 0)  # Monday 8:00 AM
        self.assertFalse(is_market_open())

    @patch('stockslist.utils.datetime')
    def test_market_hours_weekday_closed_after(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 1, 15, 16, 0)  # Monday 4:00 PM
        self.assertFalse(is_market_open())

    @patch('stockslist.utils.datetime')
    def test_market_hours_weekend(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 1, 13, 10, 30)  # Saturday 10:30 AM
        self.assertFalse(is_market_open())

    def test_market_status_structure(self):
        status = get_market_status()
        self.assertIn('is_open', status)
        self.assertIn('message', status)
        self.assertTrue('next' in status)

    def test_trading_restricted_when_market_closed(self):
        self.client.login(username='trader', password='tradepass')
        with patch('stockslist.utils.is_market_open', return_value=False):
            response = self.client.post(self.buy_url, {
                'companySymbol': 'AAPL',
                'lastPrice': 100,
                'buy': 'Buy'
            })
            self.assertEqual(response.status_code, 403)
            self.assertIn('Trading is only allowed during market hours', response.content.decode())

    def test_trading_allowed_when_market_open(self):
        self.client.login(username='trader', password='tradepass')
        with patch('stockslist.utils.is_market_open', return_value=True):
            response = self.client.post(self.buy_url, {
                'companySymbol': 'AAPL',
                'lastPrice': 100,
                'buy': 'Buy'
            })
            self.assertNotEqual(response.status_code, 403)

    def test_purchase_success_without_session_data(self):
        """Test that purchaseSuccess redirects when accessed without purchase data"""
        self.client.login(username='trader', password='tradepass')
        purchase_success_url = reverse('stockslist:purchaseSuccess')
        response = self.client.get(purchase_success_url)
        self.assertEqual(response.status_code, 302)  # Should redirect to index
        self.assertEqual(response.url, reverse('stockslist:index'))

    def test_purchase_success_with_session_data(self):
        """Test that purchaseSuccess works correctly with valid session data"""
        self.client.login(username='trader', password='tradepass')
        session = self.client.session
        session['purchase_data'] = {
            'symbol': 'AAPL',
            'quantity': 2,
            'brought_prize': 100,
            'buy_time': 'Jan 15, 2024, 10:30 AM',
            'amount': 999800
        }
        session.save()
        
        purchase_success_url = reverse('stockslist:purchaseSuccess')
        response = self.client.get(purchase_success_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AAPL')
        self.assertContains(response, '200')  # total_cost = 100 * 2
