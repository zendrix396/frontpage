from django.db import models

# Create your models here.
class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20, unique=True)
    dayHigh = models.CharField(max_length=20)
    dayLow = models.CharField(max_length=20)
    lastPrice = models.CharField(max_length=20)
    pChange = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.symbol} - {self.name}"