import os
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Max
from django.utils import timezone
from decimal import Decimal
import json
from typing import Any

from .forms import UserSignUpForm, UserLoginForm
from .models import Profile, Item, Bid, Question, Reply

def get_frontend_url():
    return os.getenv('FRONTEND_URL', 'http://localhost:5173')

def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})


# === Auth views (Emir's work) ===

@require_http_methods(["GET", "POST"])
def signup(request: HttpRequest):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect(get_frontend_url())
    else:
        form = UserSignUpForm()
    return render(request, 'api/signup.html', {'form': form})

@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(get_frontend_url())
            form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, 'api/login.html', {'form': form})

@require_http_methods(["GET"])
def logout_view(request: HttpRequest):
    logout(request)
    return redirect(get_frontend_url())

@login_required
@require_http_methods(["GET", "POST"])
def profile(request: HttpRequest):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == "GET":
        profile_image_url = profile.profile_image.url if profile.profile_image else None
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": profile.date_of_birth or "",
            "profile_image_url": profile_image_url,
        })

    # POST method - update profile
    try:
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()

        dob = request.POST.get("date_of_birth")
        if dob:
            profile.date_of_birth = dob
        
        if "profile_image" in request.FILES:
            if profile.profile_image:
                profile.profile_image.delete()
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        profile_image_url = profile.profile_image.url if profile.profile_image else None
        return JsonResponse({
            "success": True,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": str(profile.date_of_birth) if profile.date_of_birth else "",
            "profile_image_url": profile_image_url,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def user_info(request: HttpRequest):
    """Return current user info for auth check without redirecting."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False}, status=401)
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'authenticated': True,
    })


# === Item & Bid views (Krish's work) ===

@require_http_methods(["GET"])
def item_list(request: HttpRequest) -> JsonResponse:
    """List all items with optional search query."""
    search = request.GET.get('search', '').strip()
    
    items = Item.objects.all()
    
    if search:
        items = items.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Annotate with current bid
    items = items.annotate(
        highest_bid=Max('bids__amount')
    )
    
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'owner': item.owner.id,
            'title': item.title,
            'description': item.description,
            'starting_price': str(item.starting_price),
            'current_price': str(item.highest_bid if item.highest_bid else item.starting_price),
            'image_url': item.image_url or '',
            'ends_at': item.ends_at.isoformat(),
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
        })
    
    return JsonResponse({'items': data})


@csrf_exempt
@require_http_methods(["POST"])
def item_create(request: HttpRequest) -> JsonResponse:
    """Create a new auction item."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Validate required fields
    required = ['title', 'description', 'starting_price', 'ends_at']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return JsonResponse({'error': f'Missing fields: {", ".join(missing)}'}, status=400)
    
    # TODO: Replace with actual authenticated user once auth is ready
    # Temporarily use first superuser for testing
    from django.contrib.auth import get_user_model
    User = get_user_model()
    owner = User.objects.filter(is_superuser=True).first()
    if not owner:
        owner = User.objects.first()
    if not owner:
        return JsonResponse({'error': 'No users in database - create superuser first'}, status=400)
    
    try:
        from django.utils.dateparse import parse_datetime
        ends_at_str = data['ends_at']
        # Try parsing ISO format datetime
        ends_at = parse_datetime(ends_at_str)
        if not ends_at:
            # Fallback: try adding timezone info if missing
            from datetime import datetime
            ends_at = datetime.fromisoformat(ends_at_str.replace('Z', '+00:00'))
        
        item = Item.objects.create(
            owner=owner,
            title=data['title'],
            description=data['description'],
            starting_price=Decimal(data['starting_price']),
            image_url=data.get('image_url', ''),
            ends_at=ends_at,
        )
        
        return JsonResponse({
            'id': item.id,
            'owner': item.owner.id,
            'title': item.title,
            'description': item.description,
            'starting_price': str(item.starting_price),
            'current_price': str(item.starting_price),
            'image_url': item.image_url,
            'ends_at': item.ends_at.isoformat(),
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def bid_create(request: HttpRequest) -> JsonResponse:
    """Create a new bid on an item with validation."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Validate required fields
    if 'item_id' not in data or 'amount' not in data:
        return JsonResponse({'error': 'Missing item_id or amount'}, status=400)
    
    # TODO: Replace with actual authenticated user once auth is ready
    # Temporarily use first superuser for testing
    from django.contrib.auth import get_user_model
    User = get_user_model()
    bidder = User.objects.filter(is_superuser=True).first()
    if not bidder:
        bidder = User.objects.first()
    if not bidder:
        return JsonResponse({'error': 'No users in database - create superuser first'}, status=400)
    
    try:
        item = Item.objects.get(id=data['item_id'])
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    # Check auction hasn't ended
    if item.ends_at < timezone.now():
        return JsonResponse({'error': 'Auction has ended'}, status=400)
    
    # Validate bid amount
    amount = Decimal(data['amount'])
    current_price = item.current_price
    
    if amount <= current_price:
        return JsonResponse({
            'error': f'Bid must be greater than current price of {current_price}'
        }, status=400)
    
    try:
        bid = Bid.objects.create(
            item=item,
            bidder=bidder,
            amount=amount,
        )
        
        return JsonResponse({
            'id': bid.id,
            'item': bid.item.id,
            'bidder': bid.bidder.id,
            'amount': str(bid.amount),
            'created_at': bid.created_at.isoformat(),
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect(get_frontend_url())
    else:
        form = UserSignUpForm()
    return render(request, 'api/signup.html', {'form': form})

@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(get_frontend_url())
            form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, 'api/login.html', {'form': form})

@require_http_methods(["GET"])
def logout_view(request: HttpRequest):
    logout(request)
    return redirect(get_frontend_url())

@login_required
@require_http_methods(["GET", "POST"])  # Change PUT to POST
def profile(request: HttpRequest):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == "GET":
        profile_image_url = profile.profile_image.url if profile.profile_image else None
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": profile.date_of_birth or "",
            "profile_image_url": profile_image_url,
        })

    # POST method - update profile
    try:
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()

        dob = request.POST.get("date_of_birth")
        if dob:
            profile.date_of_birth = dob
        
        if "profile_image" in request.FILES:
            if profile.profile_image:
                profile.profile_image.delete()
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        profile_image_url = profile.profile_image.url if profile.profile_image else None
        return JsonResponse({
            "success": True,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": str(profile.date_of_birth) if profile.date_of_birth else "",
            "profile_image_url": profile_image_url,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def user_info(request: HttpRequest):
    """Return current user info for auth check without redirecting."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False}, status=401)
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'authenticated': True,
    })
>>>>>>> origin/main
