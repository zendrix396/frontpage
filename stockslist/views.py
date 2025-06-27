from django.shortcuts import render, get_object_or_404,redirect
# Create your views here.
from django.views.generic.base import TemplateView
from nsepython import *
from .models import Stock
from authorization.models import UserCreds
class Index(TemplateView):
    template_name = 'stockslist/index.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['data'] = Stock.objects.all()
        context['fetchUser'] = self.request.user if self.request.user.is_authenticated else None
        return context
def buy(request):
    try:
        companySymbol = request.POST.get("companySymbol")
        lastPrice = request.POST.get("lastPrice")
        buyOrSell = request.POST.get("buy")
        
    except:
        request.session['error_message'] = "Cannot fetch data"
        return redirect("stockslist:index")
