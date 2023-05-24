import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib import messages

from .helpers import format_string_as_int, format_to_currency, ListingNotActive, BidTooLow, ObjectAlreadyInDatabase
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
            data = json.loads(request.body)
            last_bid = Bid.objects.get(pk=last_bid_id)
            bid = int(format_string_as_int(data['bid']))
            if not last_bid.listing.active: raise ListingNotActive
            if bid <= last_bid.price: raise BidTooLow
            new_bid = Bid.objects.create(
                price = bid,
                user = request.user,
                listing = last_bid.listing
            )
            new_bid.save()
            exception_flag = False
        except json.JSONDecodeError:
            message = "JSON error"
        except (Bid.DoesNotExist, Bid.MultipleObjectsReturned):
            message = "Database query error"
        except ValueError:
            message = "Bid must be a number"
        except ListingNotActive: 
            message = "Auction is closed, listing no longer active"
        except BidTooLow:
            message = "Your bid should be greater than the last bid"
        except Exception as e:
            print(e)
            message = "Can't place bid"
        finally:
            if exception_flag:
                return JsonResponse({'error': message}, status=403)
           
        message = "Bid placed, you are ahead to get that item!"
        return JsonResponse({'bid': format_to_currency(bid), 'message': message})    


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
def watchlist_change_state(request, listing_id: int):
    if request.method == "POST":
        user = request.user
        listing = get_object_or_404(Listing, pk=listing_id)                 
        data = json.loads(request.body)

        if data.get('watchlist'):
            action = "delete"
            try:
                exception_flag = True
                delete = Watchlist.objects.get(user=user, listing=listing)
                delete.delete()
                exception_flag = False
            except Watchlist.DoesNotExist:
                message = "Cannot delete from watchlist: entry does not exist"
                raise ObjectDoesNotExist("Watchlist entry does not exist")
            except Exception as e:
                message = "An error occurred while deleting from watchlist"
                raise e
            finally:
                if exception_flag:
                    return JsonResponse({'error': message}, status=403)
        else:
            action = "add"
            try:
                exception_flag = True
                if Watchlist.objects.filter(user=user, listing=listing): raise ObjectAlreadyInDatabase
                add = Watchlist.objects.create(user=user, listing=listing) 
                add.save()
                exception_flag = False
            except ObjectAlreadyInDatabase:
                message = "Watchlist entry already in database"
                raise ObjectAlreadyInDatabase("Watchlist entry already in database")
            except Watchlist.DoesNotExist:
                message = "Cannot add to watchlist: entry does not exist"
                raise ObjectDoesNotExist("Watchlist entry does not exist")
            except Exception as e:
                message = "An error occurred while adding to watchlist"
                raise e
            finally:
                if exception_flag:
                    return JsonResponse({'error': message}, status=403)
            
        return JsonResponse({'action': action})
    

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