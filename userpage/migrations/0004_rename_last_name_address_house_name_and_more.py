# Generated by Django 5.0.2 on 2024-02-28 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userpage', '0003_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='last_name',
            new_name='house_name',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='first_name',
            new_name='name',
        ),
    ]