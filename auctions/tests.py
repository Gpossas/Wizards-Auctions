from django.test import TestCase, Client
from django.urls import reverse
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
        self.client = Client()
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
        self.client.login(username="Alvo Dumbledore", password="123")
        response = self.client.get(reverse('watchlist'))
        self.assertEqual(response.status_code, 200)

    def test_user_not_logged(self):
        """
        return True if user is redirect to login page
        """
        response = self.client.get(reverse('watchlist'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={reverse('watchlist')}")
        response = self.client.post(reverse('watchlist_form', args=[self.potion.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={reverse('watchlist_form', args=[self.potion.id])}")
    
    def test_valid_watchlist_form_add(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('watchlist_form', args=[self.potion.id]), {'watchlist': ''})
        self.assertEqual(response.status_code, 302)

        watchlist = Watchlist.objects.get(user=self.user, listing=self.potion)
        self.assertIsNotNone(watchlist)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Added to watchlist")
    
    def test_invalid_watchlist_form_add(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('watchlist_form', args=[0]), {'watchlist': ''})
        self.assertEqual(response.status_code, 404)

    def test_watchlist_form_deletion(self):
        Watchlist.objects.create(user=self.user, listing=self.potion)

        self.client.force_login(self.user)
        response = self.client.post(reverse('watchlist_form', args=[self.potion.id]), {'watchlist': 'True'})
        self.assertEqual(response.status_code, 302)

        # assert that is not in watchlist anymore
        with self.assertRaises(Watchlist.DoesNotExist):
            Watchlist.objects.get(user=self.user, listing=self.potion)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Deleted from watchlist")
    
    def test_fail_watchlist_form_deletion(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('watchlist_form', args=[self.potion.id]), {'watchlist': 'True'})
        self.assertEqual(response.status_code, 302)

        # assert that is not in watchlist
        with self.assertRaises(Watchlist.DoesNotExist):
            Watchlist.objects.get(user=self.user, listing=self.potion)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Can't delete from watchlist")

class BidTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Alvo Dumbledore", password="123")
        self.listing = Listing.objects.create(title="Invisibility Cloak", author=self.user)
        Bid.objects.create(price=1, user=self.user, listing=self.listing)
        Bid.objects.create(price=2, user=self.user, listing=self.listing)
        self.max_bid = Bid.objects.create(price=4, user=self.user, listing=self.listing)
    
    def test_valid_bid(self):
        """
        return True when the price is higher than the maximum bid for the listing
        """
        bid = Bid.objects.create(price=self.max_bid.price + 1, user=self.user, listing=self.listing)
        self.assertTrue(bid.is_valid_bid())
    
    def test_invalid_bid(self):
        """
        return False when the price is lower than the maximum bid for the listing
        """
        bid = Bid.objects.create(price=self.max_bid.price - 1, user=self.user, listing=self.listing)
        self.assertFalse(bid.is_valid_bid())
    
    def test_bid_has_same_price_than_max(self):
        """
        return False when the price is equal to the maximum bid for the listing
        """
        bid = Bid.objects.create(price=self.max_bid.price, user=self.user, listing=self.listing)
        self.assertFalse(bid.is_valid_bid())

    # views
    def test_valid_place_bid(self):
        client = Client()
        client.force_login(self.user)
        response = client.post(reverse('place_bid', args=[self.max_bid.id]), {'bid': self.max_bid.price + 1})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Bid placed, you are ahead to get that item!")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[self.listing.id])}")

    def test_place_bid_invalid_bid(self):
        client = Client()
        client.force_login(self.user)
        response = client.post(reverse('place_bid', args=[self.max_bid.id]), {'bid': 'venice'})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Bid must be a number")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[self.listing.id])}")
    
    def test_place_bid_inative_auction(self):
        client = Client()
        client.force_login(self.user)
        self.listing.active = False
        self.listing.save()
        response = client.post(reverse('place_bid', args=[self.max_bid.id]), {'bid': self.max_bid.price + 1})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Auction is closed, listing no longer active")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[self.listing.id])}")
    
    def test_place_bid_smaller_than_last(self):
        client = Client()
        client.force_login(self.user)
        response = client.post(reverse('place_bid', args=[self.max_bid.id]), {'bid': self.max_bid.price - 1})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your bid should be greater than the last bid")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[self.listing.id])}")

class CommentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="Alvo Dumbledore", password="123")
        self.listing = Listing.objects.create(title="Invisibility Cloak", author=self.user)
    
    def test_is_blank(self):
        c = Comments.objects.create(text='', user=self.user, listing=self.listing)
        self.assertTrue(c.is_blank())
    
    def test_text(self):
        c = Comments.objects.create(text='I love this magic wand!', user=self.user, listing=self.listing)
        self.assertEqual(c.text, "I love this magic wand!")
    
    # views
    def test_add_comments(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('comments', args=[self.listing.id]), {'comment': 'hello world'})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Added comment")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[self.listing.id])}")

    def test_blank_comments(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('comments', args=[self.listing.id]), {'comment': ''})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You can't leave blank comments")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[self.listing.id])}")

class CommentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="Alvo Dumbledore", password="123")
        self.user_2 = User.objects.create_user(username="Tom Riddle", password="123")
        self.listing = Listing.objects.create(title="Invisibility Cloak", author=self.user)
    