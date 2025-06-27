from django.shortcuts import render, get_object_or_404,redirect
# Create your views here.
from django.views.generic.base import TemplateView
from django.views import generic
from nsepython import *
from .models import Stock
from django.db.models import F
from authorization.models import UserCreds, StockOwnership
class Index(TemplateView):
    template_name = 'stockslist/index.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['data'] = Stock.objects.all()
        context['fetchUser'] = self.request.user if self.request.user.is_authenticated else None
        return context
def confirmPurchase(request):
    try:
        quantity = int(request.POST.get('quantity'))
        last_price = float(request.POST.get('lastPrice'))
        cost = quantity* last_price
        symbol = request.POST.get("symbol")
    except:
        return render(request, 'stockslist/buyStock.html', context={'error_message':"Please fill the input fields properly!"})
    buying_user = get_object_or_404(UserCreds, username=request.user.username)
    
    buying_user.amount = F("amount")-cost
    buying_user.save()
    buying_user.refresh_from_db()
    stock, created = StockOwnership.objects.get_or_create(
        user=buying_user, symbol=symbol, defaults={'quantity':quantity, 'average_price':last_price}
    )
    if not created:
        total_existing_cost = stock.quantity * stock.average_price
        total_new_cost = quantity*last_price
        total_quantity = stock.quantity + quantity
        stock.average_price = (total_existing_cost+total_new_cost)/total_quantity
        stock.quantity=total_quantity
        stock.save()
    return render(request, 'stockslist/successBuy.html', context={'user':buying_user, 'stock':stock})
def buy(request):
    try:
        companySymbol = request.POST.get("companySymbol")
        lastPrice = float(request.POST.get("lastPrice"))
        buyCheck = True if "buy" in request.POST else False if "sell" in request.POST else None
    except:
        request.session['error_message'] = "Cannot fetch data"
        return redirect("stockslist:index")
    print(companySymbol)
    print(lastPrice)
    print(buyCheck)
    userBudget = get_object_or_404(UserCreds, username=request.user.username).amount
    context = {'stock':{'symbol':companySymbol, 'lastPrice':lastPrice, 'budget':userBudget}}
    if buyCheck:
        maxStockBuy = userBudget//lastPrice
        context['stock']['maxStockBuy'] = int(maxStockBuy)
        return render(request, "stockslist/buyStock.html", context=context)