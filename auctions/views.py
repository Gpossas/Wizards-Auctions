from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib import messages

from .helpers import format_string_as_int, ListingNotActive, BidTooLow
from .models import User, Listing, Category, Watchlist, Bid, Comments

#TODO: fazer uma pagina padrão pra trouxas(quem não ta logado) com listing normais e chatos

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
    })


# =============== LISTING =============== 
@login_required
def create_listing(request):
    if request.method == "POST":
        try:
            exception_flag = True
            category = Category.objects.get(pk=request.POST["category"]) if request.POST["category"] != '' else None
            listing_data = {
                'title': request.POST["title"],
                'author': request.user,
                'description': request.POST["description"],
                'picture': request.POST["picture"],
                'category': category
            }
            # only put attributes with values, otherwise use default values from database
            listing_data = {attribute:value for attribute,value in listing_data.items() if value}
            
            price = format_string_as_int(request.POST["price"])
            listing = Listing.objects.create(**listing_data)
            bid = Bid.objects.create(
                price = price,
                user = listing_data["author"],
                listing = listing
            )
            listing.save()
            bid.save()
            exception_flag = False
        except Category.DoesNotExist:
            messages.error(request, "Select one of the listed categories")
        except ValueError:
            messages.error(request, "Price must be numeric")            
        except:
            messages.error(request, "Can't create listing")
        finally:
            if exception_flag:
                return redirect(reverse('create_listing'))
        
        messages.success(request, 'Listing created!')
        return redirect(reverse("index"))
    else:
        categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {"categories":categories})
    

def listing_page(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    try: 
        watchlist = Watchlist.objects.get(listing=listing, user=request.user) 
    except (ObjectDoesNotExist, TypeError): 
        watchlist = False

    return render(request, "auctions/listing_page.html", {
        "listing":listing,
        "in_watchlist": watchlist,
        "comments": Comments.objects.filter(listing=listing)
    })

@login_required
def listing_state(request, listing_id):
    """
    open or close an auction by changing listing.active
    """
    
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        if request.user != listing.author:
            raise PermissionDenied

        if request.POST["active"]:
            listing.active = False
            listing.save()
            messages.success(request, "Auction closed")
        else:
            listing.active = True
            listing.save()
            messages.success(request, "Auction reopen")
        return redirect(reverse('listing_page', args=[listing_id]))


# =============== COMMENTS ===============
@login_required
def comments(request, listing_id):
    if request.method == "POST":
        if not request.POST["comment"] or request.POST["comment"].isspace():
            messages.error(request, "You can't leave blank comments")
            return redirect(reverse('listing_page', args=[listing_id]))

        comment = Comments.objects.create(
            text = request.POST["comment"],
            user = request.user,
            listing = Listing.objects.get(pk=listing_id)
        )
        comment.save()

        messages.success(request, "Added comment")
        return redirect(reverse('listing_page', args=[listing_id]))

# =============== BID ===============
@login_required
def place_bid(request, last_bid_id):
    if request.method == "POST":
        try:
            exception_flag = True
            last_bid = Bid.objects.get(pk=last_bid_id)
            bid = int(format_string_as_int(request.POST["bid"]))
            if not last_bid.listing.active: raise ListingNotActive
            if bid <= last_bid.price: raise BidTooLow
            bid = Bid.objects.create(
                price = bid,
                user = request.user,
                listing = last_bid.listing
            )
            bid.save()
            exception_flag = False
        except (Bid.DoesNotExist, Bid.MultipleObjectsReturned):
            raise Http404
        except ValueError:
            messages.error(request, "Bid must be a number")
        except ListingNotActive: 
            messages.error(request, "Auction is closed, listing no longer active")
        except BidTooLow:
            messages.error(request, "Your bid should be greater than the last bid")
        except:
            messages.error(request, "Can't place bid")
        finally:
            if exception_flag:
                return redirect(reverse('listing_page', args=[last_bid.listing.id]))
           
        messages.success(request, "Bid placed, you are ahead to get that item!")
        return redirect(reverse('listing_page', args=[last_bid.listing.id]))         


# =============== CATEGORY =============== 
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories":categories})

def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = category.listings.all()
    return render(request, "auctions/index.html", {"listings":listings})


# =============== WATCHLIST =============== 
@login_required
def watchlist(request):
    user = get_object_or_404(User, pk=request.user.id)
    watchlist = Watchlist.objects.filter(user=user)
    return render(request, "auctions/watchlist.html", {"watchlist":watchlist})

@login_required
def watchlist_form(request, listing_id):
    if request.method == "POST":
        user = get_object_or_404(User, pk=request.user.id)
        listing = get_object_or_404(Listing, pk=listing_id)
        
        if request.POST["watchlist"]:
            action = "Deleted from watchlist"
            try:
                delete = Watchlist.objects.get(user=user, listing=listing)
                delete.delete()
            except:
                messages.error(request, "Can't delete from watchlist")
                return redirect(reverse('listing_page', kwargs={'listing_id': listing_id}))
        else:
            action = "Added to watchlist"
            try:
                add = Watchlist.objects.create(user=user, listing=listing) 
                add.save()
            except:
                messages.error(request, "Can't add to watchlist")
                return redirect(reverse('listing_page', kwargs={'listing_id': listing_id}))
        
        messages.success(request, action)
        return redirect(reverse('listing_page', kwargs={'listing_id': listing_id}))
    

# =============== LOGIN =============== 
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return redirect(request.META.get('HTTP_REFERER'))

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return redirect(request.META.get('HTTP_REFERER'))
        
        login(request, user)
        messages.success(request, "these listings are cooler ;)")
        return redirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")