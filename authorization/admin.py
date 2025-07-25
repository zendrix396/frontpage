from django.contrib import admin
from .models import UserCreds, StockOwnership
# Register your models here.

admin.site.register(UserCreds)
admin.site.register(StockOwnership)