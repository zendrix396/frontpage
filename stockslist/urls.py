from django.urls import path

from . import views
app_name = "stockslist"
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('buy/', views.buy, name='buy'),
    path('confirmPurchase/', views.confirmPurchase, name='confirmPurchase'),
    path('api/liveapi', views.stock_data_json, name='live_api'),
]