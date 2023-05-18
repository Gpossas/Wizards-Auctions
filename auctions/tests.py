from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.http import Http404
from django.urls import reverse
# from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.contrib.messages import get_messages
from .models import *

# Create your tests here.
class CategoryTestCase(TestCase):
    def setUp(self):
        # create categories
        p = Category.objects.create(name="potions")
        b = Category.objects.create(name="brooms")
        Category.objects.create(name="dark arts")

        self.user = User.objects.create_user(username="Alvo Dumbledore", password="123")
        # create listings
        Listing.objects.create(title="Invisibility Cloak", author=self.user)
        self.amortentia = Listing.objects.create(title="Amortentia", category=p, author=self.user)
        Listing.objects.create(title="Polyjuice Potion", category=p, author=self.user)
        Listing.objects.create(title="Nimbus 2000", category=b, author=self.user)

    def test_category_name(self):
        """
        Test if the category name is set correctly
        """
        potions = Category.objects.get(name="potions")
        self.assertEqual(potions.name, "potions")
    
    def test_category_name_uniqueness(self):
        """
        Test if category names must be unique
        """
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="potions")
    
    def test_listing_count(self):
        """
        test_listing_count() return True if the counting of listings in a category is correct
        """
        potions = Category.objects.get(name="potions")
        self.assertEqual(potions.listings.count(), 2)
    
    def test_category_listing_relationship_null(self):
        """
        Test if a listing can have a null category
        """
        listing = Listing.objects.create(title="Invisibility Cloak", author=self.user)

        self.assertIsNone(listing.category)
    

    # views
    def test_categories_showing(self):
        """
        test_categories_showing() return True if all categories are being shown
        """
        c = Client()
        response = c.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["categories"].count(), 3)

    def test_valid_category_page(self):
        pk = self.amortentia.id
        c = Client()
        response = c.get(reverse('category', args=[pk]))
        self.assertEqual(response.status_code, 200)

    def test_invalid_category_raises_http404(self):
        c = Client()
        invalid_index = 0
        response = c.get(reverse('category', args=[invalid_index]))
        self.assertEqual(response.status_code, 404)
    
    def test_category_listing_count(self):
        """
        return True if all listings related to a category is shown
        """
        c = Client()
        response = c.get(reverse('category', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["listings"].count(), 2)


class WatchlistTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Alvo Dumbledore", password="123")
        self.user_2 = User.objects.create_user(username="Tom Riddle", password="123")
        # create listings
        self.cloak = Listing.objects.create(title="Invisibility Cloak", author=self.user)
        self.amortentia = Listing.objects.create(title="Amortentia", author=self.user)
        self.potion = Listing.objects.create(title="Polyjuice Potion", author=self.user)
        self.nimbus = Listing.objects.create(title="Nimbus 2000", author=self.user)
    
    def test_valid_watchlist(self):
        try:
            Watchlist.objects.create(user=self.user, listing=self.amortentia)
        except Exception as e:
            raise ValueError(f"Error occurred while creating a watchlist: {e}")
    
    def test_count_listing_watchlist(self):
        """
        return True if the count of listings in user watchlist is correct
        """
        Watchlist.objects.create(user=self.user, listing=self.cloak)
        Watchlist.objects.create(user=self.user, listing=self.nimbus)
        Watchlist.objects.create(user=self.user_2, listing=self.potion)

        listings = Watchlist.objects.filter(user=self.user)
        self.assertEqual(listings.count(), 2)
    
    # views
    def test_valid_user(self):
        c = Client()
        c.login(username="Alvo Dumbledore", password="123")
        response = c.get(reverse('watchlist'))
        self.assertEqual(response.status_code, 200)

    def test_user_not_logged(self):
        """
        return True if user is redirect to login page
        """
        c = Client()
        response = c.get(reverse('watchlist'))
        self.assertEqual(response.status_code, 302)
        response = c.post(reverse('watchlist_form', args=[1]))
        self.assertEqual(response.status_code, 302)
    
    def test_valid_watchlist_form_add(self):
        c = Client()
        c.force_login(self.user)
        response = c.post(reverse('watchlist_form', args=[self.potion.id]), {'watchlist': ''})
        self.assertEqual(response.status_code, 302)

        watchlist = get_object_or_404(Watchlist, user=self.user, listing=self.potion)
        self.assertIsNotNone(watchlist)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Added to watchlist")