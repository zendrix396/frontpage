from django.db import models

# Create your models here.
class UserCreds(models.Model):
    username = models.CharField(max_length=20) 
    email = models.EmailField("this is email field")
    amount = models.FloatField(default=1000000.00)

class StockOwnership(models.Model):
    user = models.ForeignKey("UserCreds",on_delete=models.CASCADE, related_name='owned_stocks')
    symbol = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=0)
    brought_prize = models.FloatField(default=0)
    buy_time = models.DateTimeField(auto_now_add=True)
    profit = models.FloatField(default=0)
    def __str__(self):
        return f"{self.symbol} x {self.quantity}"