from django.db import models


# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


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

   
