# Generated by Django 5.0.2 on 2024-03-12 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_order_discount_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('cancelled', 'Cancelled'), ('delivered', 'Delivered'), ('return_requested', 'Return Requested'), ('returned', 'Returned')], default='pending', max_length=20),
        ),
    ]
