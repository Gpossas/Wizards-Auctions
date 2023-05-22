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
        c = Comments.objects.create(text=' ', user=self.user, listing=self.listing)
        self.assertTrue(c.is_blank())
        c = Comments.objects.create(text='  ', user=self.user, listing=self.listing)
        self.assertTrue(c.is_blank())
        c = Comments.objects.create(text='\n', user=self.user, listing=self.listing)
        self.assertTrue(c.is_blank())
    
    def test_text(self):
        c = Comments.objects.create(text='I love this magic wand!', user=self.user, listing=self.listing)
        self.assertEqual(str(c), "I love this magic wand!")
    
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
        response = self.client.post(reverse('comments', args=[self.listing.id]), {'comment': ' '})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You can't leave blank comments")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[self.listing.id])}")

class ListingsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Alvo Dumbledore", password="123")
        self.client = Client()
        self.client.force_login(self.user)
        self.user_2 = User.objects.create_user(username="Tom Riddle", password="123")
        self.category = Category.objects.create(name="clothing")
        self.listing = Listing.objects.create(
            title="Invisibility Cloak", 
            author=self.user,
            description="where am I lol",
            picture="cloak.jpg",
            category=self.category,
            active=False
        )
        Bid.objects.create(price=1, listing=self.listing, user=self.user)

    def test_listing_creation(self):
        """
        Test that a listing is created correctly
        """
        self.assertEqual(self.listing.title, "Invisibility Cloak")
        self.assertEqual(self.listing.author, self.user)
        self.assertEqual(self.listing.description, "where am I lol")
        self.assertEqual(self.listing.picture, "cloak.jpg")
        self.assertEqual(self.listing.category, self.category)
        self.assertEqual(self.listing.active, False)
    
    def test_listing_string_representation(self):
        """
        Test the string representation of a listing
        """
        self.assertEqual(str(self.listing), "Invisibility Cloak")
    
    def test_listing_text_blank(self):
        """
        Test if listing text is blank
        """
        self.assertFalse(self.listing.is_blank())
        self.assertTrue(Listing.objects.create(title="", author=self.user).is_blank())
        self.assertTrue(Listing.objects.create(title=" ", author=self.user).is_blank())
        self.assertTrue(Listing.objects.create(title="\n", author=self.user).is_blank())
    
    def test_listing_category_relation(self):
        """
        Test the relation between a listing and its category
        """
        self.assertEqual(self.listing.category.name, "clothing")
        self.assertIn(self.listing, self.category.listings.all())

    def test_listing_author_relation(self):
        """
        Test the relation between a listing and its author
        """
        self.assertEqual(self.listing.author.username, "Alvo Dumbledore")
        self.assertIn(self.listing, self.user.author_listings.all())
    
    # views
    def test_listing_state_not_logged(self):
        client = Client()
        response = client.post(reverse('listing_state', args=[self.listing.id]), {'active': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={reverse('listing_state', args=[self.listing.id])}")


    def test_listing_state_error_listing(self):
        """
        Raise error if query don't return listing
        """
        response = self.client.post(reverse('listing_state', args=[0]))
        self.assertEqual(response.status_code, 404)
    
    def test_listing_state_active(self):
        """
        return True if it change from true to false state and close auction
        """
        listing = Listing.objects.create(active=True, title='potion', author=self.user)

        response = self.client.post(reverse('listing_state', args=[listing.id]), {'active': 'True'})
        self.assertEqual(response.status_code, 302)
        state_before = listing.active
        state_after = Listing.objects.get(pk=listing.id).active
        self.assertNotEqual(state_before, state_after)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Auction closed")
        self.assertEqual(messages[0].tags, "success")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[listing.id])}")
    
    def test_listing_state_inactive(self):
        """
        return True if it change from state false to true and reopen auction
        """
        listing = Listing.objects.create(active=False, title='potion', author=self.user)

        response = self.client.post(reverse('listing_state', args=[listing.id]), {'active': ''})
        self.assertEqual(response.status_code, 302)
        state_before = listing.active
        state_after = Listing.objects.get(pk=listing.id).active
        self.assertNotEqual(state_before, state_after)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Auction reopen")
        self.assertEqual(messages[0].tags, "success")
        self.assertEqual(response.url, f"{reverse('listing_page', args=[listing.id])}")
    
    def test_listing_state_not_author(self):
        """
        return True if raise error if an user that is not the author of the auction try to change state
        """
        listing = Listing.objects.create(active=True, title='potion', author=self.user)

        self.client.force_login(self.user_2)
        response = self.client.post(reverse('listing_state', args=[listing.id]), {'active': 'True'})
        self.assertEqual(response.status_code, 403)
        # don't change state
        state_before = listing.active
        state_after = Listing.objects.get(pk=listing.id).active
        self.assertEqual(state_before, state_after)
    
    def test_creating_listing_not_logged(self):
        """
        Test if user is redirected to login if not logged
        """
        client = Client()
        response = client.get(reverse('create_listing'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={reverse('create_listing')}")

    def test_get_creating_listing(self):
        """
        Test get request to creating listing
        """
        response = self.client.get(reverse('create_listing'))
        self.assertEqual(response.context['categories'].count(), 1)
        self.assertEqual(response.status_code, 200)
    
    def test_creating_listing(self):
        """
        Test complete listing
        """
        add_listing = {
            'title': 'Invisibility Cloak',
            'price': 7890,
            'description': 'Where am I?',
            'picture': 'cloak.jpg',
            'category': self.category.id
        }
        response = self.client.post(reverse('create_listing'), add_listing)
        self.assertEqual(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Listing created!")
        self.assertEqual(messages[0].tags, "success")
        self.assertEqual(response.url, f"{reverse('index')}")
    
    def test_creating_listing_defaults(self):
        """
        Test the default values of a listing
        """
        add_listing = {
            'title': 'Invisibility Cloak',
            'price': 7890,
            'category': '',
            'description': '',
            'picture': '',
        }
        response = self.client.post(reverse('create_listing'), add_listing)
        self.assertEqual(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Listing created!")
        self.assertEqual(messages[0].tags, "success")
        self.assertEqual(response.url, f"{reverse('index')}")
    
    def test_creating_listing_invalid_category_id(self):
        """
        Test complete listing
        """
        max_id = Category.objects.all().aggregate(max_id=Max('id'))['max_id']
        add_listing = {
            'title': 'Invisibility Cloak',
            'price': 7890,
            'description': 'Where am I?',
            'picture': 'cloak.jpg',
            'category': max_id + 1
        }
        response = self.client.post(reverse('create_listing'), add_listing)
        self.assertEqual(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Select one of the listed categories")
        self.assertEqual(messages[0].tags, "error")
        self.assertEqual(response.url, f"{reverse('index')}")

    def test_not_logged_listing_page(self):
        """
        test if a not logged user can access the page
        """
        client = Client()
        response = client.get(reverse('listing_page', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)

    def test_listing_page_invalid_listing(self):
        """
        return true if invalid page response is 404
        """
        max_id = Listing.objects.all().aggregate(max_id=Max('id'))['max_id']
        response = self.client.get(reverse('listing_page', args=[max_id+1]))
        self.assertEqual(response.status_code, 404)
    
    def test_listing_page_not_in_watchlist(self):
        response = self.client.get(reverse('listing_page', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['in_watchlist'])
    
    def test_listing_page_in_watchlist(self):
        in_watchlist = Watchlist.objects.create(listing=self.listing, user=self.user)

        response = self.client.get(reverse('listing_page', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['in_watchlist'], in_watchlist)
    
    def test_listing_page_not_added_to_other_users(self):
        """
        test when a user add a listing to watchlist, this listing is not added to the watchlist of another user
        """
        Watchlist.objects.create(listing=self.listing, user=self.user)
        self.client.force_login(self.user_2)
        response = self.client.get(reverse('listing_page', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['in_watchlist'])

    def test_listing_page_comments(self):
        """
        test number of comments, text and only show the comments of this listing
        """
        Comments.objects.create(text='nice cloak 0_0', listing=self.listing, user=self.user)

        ankh_shield_listing = Listing.objects.create(title='ankh shield', author=self.user)
        Bid.objects.create(price=1, user=self.user, listing=ankh_shield_listing)
        Comments.objects.create(text='Terrarian!', listing=ankh_shield_listing, user=self.user)
        Comments.objects.create(text='eye of cthulhu', listing=ankh_shield_listing, user=self.user)

        response = self.client.get(reverse('listing_page', args=[ankh_shield_listing.id]))
        self.assertEqual(response.context['comments'].count(), 2)
        self.assertEqual(str(response.context['comments'][0]), 'Terrarian!')
    
    def test_index_page(self):
        Listing.objects.create(title='ankh shield', author=self.user)
        Listing.objects.create(title='speed boots', author=self.user)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['listings'].count(), 3)