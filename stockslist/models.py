from django.db import models

# Create your models here.
class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20, unique=True)
    dayHigh = models.FloatField(max_length=20)
    dayLow = models.FloatField(max_length=20)
    lastPrice = models.FloatField(max_length=20)
    pChange = models.FloatField(max_length=20)
    # base_price = models.IntegerField()
    def __str__(self):
        return f"{self.symbol} - {self.name}"