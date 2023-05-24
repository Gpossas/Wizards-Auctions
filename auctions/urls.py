from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing_page/<int:listing_id>", views.listing_page, name="listing_page"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist_state/<int:listing_id>", views.watchlist_change_state, name="watchlist_change_state"),
    path("place_bid/<int:last_bid_id>", views.place_bid, name="place_bid"),
    path("listing_state/<int:listing_id>", views.listing_state, name="listing_state"),
    path("comments/<int:listing_id>", views.comments, name="comments"),
]
