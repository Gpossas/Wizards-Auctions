# Generated by Django 4.1.6 on 2023-04-24 22:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='price',
        ),
    ]
