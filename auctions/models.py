from django.contrib.auth.models import AbstractUser
from django.db.models import Max
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
    def is_blank(self):
        return not self.title or self.title.isspace()


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __str__(self) -> str:
        return f"{self.name}"


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
    def is_valid_bid(self):
        max_bid = Bid.objects.filter(listing=self.listing).exclude(pk=self.pk).aggregate(max_bid=Max('price'))['max_bid']
        return self.price > max_bid
    

class Comments(models.Model):
    text = models.TextField()
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='comments')
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return f"{self.text}"
    def is_blank(self):
        return not self.text or self.text.isspace()