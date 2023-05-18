from django.contrib import admin

class BidAdmin(admin.ModelAdmin):
    list_display = ("price", "user", "listing")
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("listing", "user")
    ordering = ["user"]

# Register your models here.
from .models import *
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Category)
admin.site.register(Bid, BidAdmin)