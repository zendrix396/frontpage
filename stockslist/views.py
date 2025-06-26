from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.views.generic.base import TemplateView
from nsepython import *
class Index(TemplateView):
    template_name = 'stockslist/index.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        positions = nsefetch('https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O')
        data = []
        for stock in positions['data']:
            company = {'name':'N/A','symbol':'N/A','dayHigh':'N/A','dayLow':'N/A','lastPrice':'N/A', "pChange":'N/A'}
            company['name'] = stock.get("meta", 'N/A')['companyName']
            company['symbol'] = stock.get("meta", 'N/A')['symbol']
            company['dayHigh'] = stock.get("dayHigh", 'N/A')
            company['dayLow'] = stock.get("dayLow", 'N/A')
            company['lastPrice'] = stock.get("lastPrice", 'N/A')
            company['pChange'] = stock.get("pChange", 'N/A')
            data.append(company)
        context['data'] = data
        return context