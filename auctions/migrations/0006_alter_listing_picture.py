# Generated by Django 4.1.6 on 2023-04-23 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_remove_watchlist_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='picture',
            field=models.TextField(blank=True, default='https://t4.ftcdn.net/jpg/04/99/93/31/360_F_499933117_ZAUBfv3P1HEOsZDrnkbNCt4jc3AodArl.jpg'),
        ),
    ]
