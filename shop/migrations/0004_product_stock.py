# Generated by Django 5.0.2 on 2024-02-28 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_product_image1_product_image2'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.BigIntegerField(null=True),
        ),
    ]