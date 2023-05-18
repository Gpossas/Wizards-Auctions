from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='author_listings') 
    description = models.TextField(blank=True)
    picture = models.TextField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='listings', blank=True, null=True)
    active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return f"{self.title}"

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __str__(self) -> str:
        return f"{self.name}"

# should user be one-to-ne since no two users share the same watchlist, or foreignKey because two users can have the same listings in their watchlist?
#TODO: update to one-to-one because we only have one watchlist per user
class Watchlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='watchlist_items')
    def __str__(self) -> str:
        return f"{self.listing} is in {self.user} watchlist"


class Bid(models.Model):
    price = models.PositiveIntegerField()
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='bids')
    def __str__(self) -> str:
        return f"{self.price}"
    

class Comments(models.Model):
    text = models.TextField()
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='comments')
    def __str__(self) -> str:
        return f"{self.text}"