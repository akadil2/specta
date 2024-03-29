# Generated by Django 5.0.2 on 2024-02-28 12:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpage', '0002_customer_is_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=12)),
                ('post', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('pin_code', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
