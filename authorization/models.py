from django.db import models

# Create your models here.
class UserCreds(models.Model):
    username = models.CharField(max_length=20) 
    email = models.EmailField("this is email field")
    amount = models.IntegerField(default=1000000)
