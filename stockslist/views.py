from django.shortcuts import render, get_object_or_404,redirect
# Create your views here.
from django.views.generic.base import TemplateView
from django.views import generic
from nsepython import *
from .models import Stock
from django.utils.timezone import localtime
from django.db.models import F
from authorization.models import UserCreds, StockOwnership
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class Index(TemplateView):
    template_name = 'stockslist/index.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['data'] = Stock.objects.all()
        context['fetchUser'] = self.request.user if self.request.user.is_authenticated else None
        return context
def confirmPurchase(request):
    try:
        symbol = request.POST.get("symbol")
        if symbol == None:
            return redirect("stockslist:index")
        quantity = int(request.POST.get('quantity'))
        last_price = float(request.POST.get('lastPrice'))
        cost = round(quantity* last_price,2)
    except:
        return render(request, 'stockslist/buyStock.html', context={'error_message':"Please fill the input fields properly!"})
    print(quantity)
    buying_user = get_object_or_404(UserCreds, username=request.user.username)
    
    buying_user.amount = F("amount")-round(cost,2)
    buying_user.save()
    buying_user.refresh_from_db()
    stock, created = StockOwnership.objects.get_or_create(
        user=buying_user, symbol=symbol, quantity=quantity, brought_prize=last_price
    )
    stock.save()
    if created:
        try:
            del request.session['purchase_data']
        except:
            pass
        request.session['purchase_data'] = {
            'symbol': stock.symbol,
            'quantity': stock.quantity,
            'brought_prize': stock.brought_prize,
            'buy_time': localtime(stock.buy_time).strftime("%b %d, %Y, %I:%M %p"),
            'amount': round(buying_user.amount,2),
        }
        return redirect('stockslist:purchaseSuccess')
@method_decorator(login_required, name='dispatch')
class Dashboard(generic.TemplateView):
    template_name = 'stockslist/dashboard.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        user = UserCreds.objects.get(username=self.request.user.username)
        owned = user.owned_stocks.all()

        stock_map = {s.symbol:s.lastPrice for s in Stock.objects.all()}
        for p in owned:
            p.last_price = stock_map.get(p.symbol, '0.0')
        context['data'] = owned
        context['user'] = user
        return context

def purchaseSuccess(request):
    purchase_data = request.session.get('purchase_data', None)
    purchase_data['total_cost'] = purchase_data['brought_prize']*purchase_data['quantity']
    purchase_data['amount_left'] = round(get_object_or_404(UserCreds, username=request.user.username).amount,2)
    if not purchase_data:
        return redirect('stockslist:index')
    return render(request, 'stockslist/successBuy.html', context={'data':purchase_data})

def buy(request):
    try:
        companySymbol = request.POST.get("companySymbol")
        lastPrice = float(request.POST.get("lastPrice"))
        buyCheck = True if "buy" in request.POST else False
    except:
        request.session['error_message'] = "Cannot fetch data"
        return redirect("stockslist:index")
    print(companySymbol)
    print(lastPrice)

    print(buyCheck)
    userBudget = round(get_object_or_404(UserCreds, username=request.user.username).amount,2)
    context = {'stock':{'symbol':companySymbol, 'lastPrice':lastPrice, 'budget':userBudget}}
    if buyCheck:
        maxStockBuy = userBudget//lastPrice
        context['stock']['maxStockBuy'] = int(maxStockBuy)
        return render(request, "stockslist/buyStock.html", context=context)
def stock_data_json(request):
    stocks = Stock.objects.all()
    data = [
        {
            "symbol": s.symbol,
            "name": s.name,
            "lastPrice": s.lastPrice,
            "dayHigh": s.dayHigh,
            "dayLow": s.dayLow,
            "pChange": s.pChange
        }
        for s in stocks
    ]
    return JsonResponse(data, safe=False)

def sell(request):
    try:
        purchase_id = request.POST.get('id')
    except Exception as e:
        return render(request, 'stockslist/dashboard.html', context={'error_message':e})
    curr_user = UserCreds.objects.get(username=request.user.username)
    stock_ownership = StockOwnership.objects.filter(id=purchase_id).first()
    print(stock_ownership)
    if not stock_ownership:
        return render(request, 'stockslist/dashboard.html', context={'error_message': "Stock not found"})
    gainLoss = stock_ownership.profit
    curr_user.realized_gain += gainLoss
    curr_user.amount+= gainLoss
    curr_user.amount+=stock_ownership.brought_prize*stock_ownership.quantity
    curr_user.unrealized_gain-=gainLoss
    curr_user.save()
    stock_ownership.delete()
    return redirect('stockslist:dashboard')
def live_profit(request):
    user_ = UserCreds.objects.get(username=request.user)
    purchase = user_.owned_stocks.all()
    data = [
        {
            'id':stock.id,
            'profit': stock.profit,
            'symbol': stock.symbol,
            'buy_time':stock.buy_time,
            'brought_prize':stock.brought_prize,
            'unrealized_gain':user_.unrealized_gain,
            'quantity':stock.quantity,
            'lastPrice':Stock.objects.get(symbol=stock.symbol).lastPrice
        }
        for stock in purchase
    ]
    return JsonResponse(data, safe=False)