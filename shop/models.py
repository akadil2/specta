from django.db import models
from userpage.models import Customer,Address
from django.db.models import Sum,F


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.BigIntegerField(null=True) 
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image1 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self) :
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def calculate_total_amount(self):
        return self.product.price * self.quantity
   

    def __str__(self):
        return self.user.username

class OrderItem(models.Model):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    CANCELLED = 'cancelled'
    DELIVERED = 'delivered'
    RETURN_REQUESTED = 'return_requested'
    RETURNED = 'returned'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SHIPPED, 'Shipped'),
        (CANCELLED, 'Cancelled'),
        (DELIVERED, 'Delivered'),
        (RETURN_REQUESTED,'Return Requested'),
        (RETURNED, 'Returned')
        
    ]

    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.status}"
    
    def calculate_amount(self):
        return self.quantity * self.product.price



class Order(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through=OrderItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    address = models.ForeignKey('userpage.Address', on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'Order #{self.pk} by {self.user.username}'
    
class Wishlist(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    

    def __str__(self):
        return self.user.username
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.PositiveIntegerField(default=100)
    min_orderamount = models.PositiveIntegerField(default=500)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.valid_from <= now <= self.valid_to

    def __str__(self):
        return self.code
