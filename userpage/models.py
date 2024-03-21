from django.db import models
from django.contrib.auth.models import AbstractUser



class Customer(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.username
    
class Address(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    house_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=12)
    post = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=20)
    state = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Wallet(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username
   
