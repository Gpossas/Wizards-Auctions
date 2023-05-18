from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from .models import User, Listing, Category, Watchlist, Bid, Comments

#TODO: fazer uma pagina padrão pra trouxas(quem não ta logado) com listing normais e chatos

def index(request):
    listings = Listing.objects.all()
    # use related_name to link bids to the respective listings instead Bids.objects because it may relate to the wrong bid and listing
    # I put .last in template because the last bid will be the max, since we only add bids >= the last
    # bids = Bid.objects.values('listing_id').annotate(bid=Max('price')).distinct()
    return render(request, "auctions/index.html", {
        "listings": listings,
        # "bids": bids
    })


# =============== LISTING =============== 
@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        price = request.POST["price"]
        author = request.user
        description = request.POST["description"]
        picture = request.POST["picture"]
        category_id = request.POST["category"]
        category = Category.objects.get(pk=category_id) if category_id else None

        # TODO: uma forma/ função para só criar com as variaveis com valor True, ex: default em models só funciona se eu não passar essa variavel aqui
        # então preciso de uma forma que só use as variaveis que tenham um valor p/ usar default em models
        try:  
            listing = Listing.objects.create(
                title=title,
                author=author,
                description=description,
                picture=picture,
                category=category
            )
            bid = Bid.objects.create(
                price = price,
                user = author,
                listing = listing
            )
            listing.save()
            bid.save()
        except:
            messages.error(request, "Can't create listing")
            return redirect(reverse('create_listing'))
        
        messages.success(request, 'Listing created!')
        return redirect(reverse("index"))
    else:
        categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {"categories":categories})
    

def listing_page(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    watchlist = True
    try: 
        Watchlist.objects.get(listing=listing, user=request.user) 
    except ObjectDoesNotExist: 
        watchlist = False

    return render(request, "auctions/listing_page.html", {
        "listing":listing,
        "in_watchlist": watchlist,
        "comments": Comments.objects.filter(listing=listing)
    })

@login_required
def listing_state(request, listing_id):
    if request.method == "POST":
        # TODO: set user permissions/authentication
        if request.POST["active"]:
            Listing.objects.filter(pk=listing_id).update(active=False)
            messages.success(request, "Auction closed")
        else:
            Listing.objects.filter(pk=listing_id).update(active=True)
            messages.success(request, "Auction reopen")
        return redirect(request.META.get('HTTP_REFERER'))


# =============== COMMENTS ===============
@login_required
def comments(request, listing_id):
    if request.method == "POST":
        if not request.POST["comment"]:
            messages.error(request, "You can't leave blank comments")
            return redirect(request.META.get('HTTP_REFERER'))

        comment = Comments.objects.create(
            text = request.POST["comment"],
            user = request.user,
            listing = Listing.objects.get(pk=listing_id)
        )
        comment.save()

        messages.success(request, "Added comment")
        return redirect(request.META.get('HTTP_REFERER'))

# =============== BID ===============
@login_required
def place_bid(request, bid_id):
    if request.method == "POST":
        bid = int(request.POST["bid"] or 0)
        last_bid = Bid.objects.get(pk=bid_id)
        
        # error handler
        if not last_bid.listing.active: 
            messages.error(request, "Auction is closed, listing no longer active")
            return redirect(request.META.get('HTTP_REFERER'))
        if bid <= last_bid.price:
            messages.error(request, "Your bid should be greater than the last bid")
            return redirect(request.META.get('HTTP_REFERER'))
        try:  
            bid = Bid.objects.create(
                price = bid,
                user = request.user,
                listing = last_bid.listing
            )
            bid.save()
        except:
            messages.error(request, "Can't place bid")
            return redirect(request.META.get('HTTP_REFERER')) 
           
        messages.success(request, "Bid placed, you are ahead to get that item!")
        return redirect(request.META.get('HTTP_REFERER'))         


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