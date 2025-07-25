from django.urls import path
from . import views

app_name = "stockslist"
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('buy/', views.buy, name='buy'),
    path('confirmPurchase/', views.confirmPurchase, name='confirmPurchase'),
    path('api/liveapi', views.stock_data_json, name='live_api'),
    path('purchaseSuccess/', views.purchaseSuccess, name='purchaseSuccess'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('api/liveprofit', views.live_profit, name='live_profit'),
    path('sell/', views.sell, name='sell'),
]