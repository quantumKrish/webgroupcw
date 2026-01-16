import os
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Max
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings 
from decimal import Decimal
from urllib.parse import urlparse
import json

from .forms import UserSignUpForm, UserLoginForm
from .models import Profile, Item, ItemImage, Bid, Question, Reply

def get_frontend_url():
    return os.getenv('FRONTEND_URL', 'http://localhost:5173')

def clean_url(url):
    if not url:
        return url
    return url.split("?")[0]

def build_absolute_url(request: HttpRequest, url: str) -> str:
    """Build absolute URL, handling both relative and absolute (S3) URLs."""
    if not url:
        return ''
    # If URL already starts with http, it's absolute (e.g., S3 URL), return as-is
    if url.startswith('http'):
        return url
    # Otherwise, make it absolute relative to the request
    return request.build_absolute_uri(url)

def get_image_url(request: HttpRequest, item: Item) -> str:
    """Build absolute URL for item image."""
    primary_image = item.images.first() if hasattr(item, 'images') else None
    if primary_image:
        return build_absolute_url(request, primary_image.image.url)
    if item.image:
        return build_absolute_url(request, item.image.url)
    if item.image_url:
        return item.image_url
    return ''

def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})

def send_winner_email(
    to_email: str,
    item: Item 
) -> None:
    subject = "🎉 Congratulations, You Won the Auction!"
    
    item_title = item.title
    item_owner = item.owner.username
    final_price = item.current_price

    message = (
        f"Dear Winner,\n\n"
        f"Congratulations! You have won the auction for the item '{item_title}' "
        f"which was listed by {item_owner}.\n\n"
        f"Winning Price: ${final_price:.2f}\n\n"
        f"Please make sure to complete the payment as soon as possible. "
        f"Details about the next steps will follow in a separate email.\n\n"
        f"Thank you for participating in our auction, and we hope to see you again soon!\n\n"
        f"Best Regards,\nThe Auction Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )


# === Auth views ===

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
        profile_image_url = build_absolute_url(request, profile.profile_image.url) if profile.profile_image else None
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": profile.date_of_birth or "",
            "profile_image_url": clean_url(profile_image_url),
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

        profile_image_url = build_absolute_url(request, profile.profile_image.url) if profile.profile_image else None
        return JsonResponse({
            "success": True,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": str(profile.date_of_birth) if profile.date_of_birth else "",
            "profile_image_url": clean_url(profile_image_url),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@require_http_methods(["GET"])
def user_info(request: HttpRequest):
    """Return current user info for auth check without redirecting."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False}, status=401)
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    profile_image_url = build_absolute_url(request, profile.profile_image.url) if profile.profile_image else None
    
    # Get won auctions (if winner field exists)
    won_items = []
    if hasattr(Item, 'winner'):
        won_auctions = Item.objects.filter(winner=user, winner_email_sent=True)
        for item in won_auctions:
            image_url = build_absolute_url(request, item.image.url) if item.image else (item.image_url or '')
            won_items.append({
                'id': item.id,
                'title': item.title,
                'image_url': clean_url(image_url),
                'final_price': str(item.current_price),
            })
    
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'profile_image_url': clean_url(profile_image_url),
        'authenticated': True,
        'won_items': won_items,
    })


@require_http_methods(["GET"])
def user_profile_display(request: HttpRequest, user_id: int) -> JsonResponse:
    """Get public user profile with their items and bids."""
    try:
        from .models import User
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    try:
        profile, _ = Profile.objects.get_or_create(user=user)
        profile_image_url = build_absolute_url(request, profile.profile_image.url) if profile.profile_image else None
        
        # Get user's items
        user_items = Item.objects.filter(owner=user).order_by('-created_at')[:10]
        items_data = []
        for item in user_items:
            image_url = ''
            if item.image:
                image_url = build_absolute_url(request, item.image.url)
            elif item.image_url:
                image_url = item.image_url
            
            highest_bid = item.bids.order_by('-amount').first()
            current_price = str(highest_bid.amount) if highest_bid else str(item.starting_price)
            
            items_data.append({
                'id': item.id,
                'title': item.title,
                'current_price': current_price,
                'image_url': clean_url(image_url),
                'ends_at': item.ends_at.isoformat(),
            })
        
        # Get user's bids
        user_bids = Bid.objects.filter(bidder=user).select_related('item').order_by('-created_at')[:10]
        bids_data = []
        for bid in user_bids:
            bids_data.append({
                'id': bid.id,
                'item_id': bid.item.id,
                'item_title': bid.item.title,
                'amount': str(bid.amount),
                'created_at': bid.created_at.isoformat(),
            })
        
        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_of_birth': str(profile.date_of_birth) if profile.date_of_birth else '',
                'profile_image_url': clean_url(profile_image_url),
            },
            'items': items_data,
            'bids': bids_data,
        })
    except Exception as e:
        print(f"ERROR in user_profile_display: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


# === Item & Bid views ===

@csrf_exempt
@require_http_methods(["GET"])
def item_list(request: HttpRequest) -> JsonResponse:
    """List all items with optional search query."""
    try:
        search = request.GET.get('search', '').strip()
        
        items = Item.objects.all().order_by('-created_at')
        
        if search:
            items = items.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        data = []
        for item in items:
            try:
                # Primary image URL (prefers ItemImage)
                image_url = get_image_url(request, item)

                
                # Get current price (highest bid or starting price)
                highest_bid = item.bids.all().order_by('-amount').first()
                current_price = str(highest_bid.amount) if highest_bid else str(item.starting_price)
                
                item_data = {
                    'id': item.id,
                    'owner': item.owner.id,
                    'owner_username': item.owner.username,
                    'title': item.title,
                    'description': item.description,
                    'starting_price': str(item.starting_price),
                    'current_price': current_price,
                    'image_url': clean_url(image_url),
                    'ends_at': item.ends_at.isoformat(),
                    'created_at': item.created_at.isoformat(),
                    'updated_at': item.updated_at.isoformat(),
                }
                data.append(item_data)
                
            except Exception as item_error:
                print(f"ERROR processing item {item.id}: {item_error}")
                continue
        
        return JsonResponse({'items': data})
        
    except Exception as e:
        print(f"ERROR in item_list: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def item_create(request: HttpRequest) -> JsonResponse:
    """Create a new auction item."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    try:
        # Parse form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        starting_price = request.POST.get('starting_price', '').strip()
        ends_at_str = request.POST.get('ends_at', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        image_file = request.FILES.get('image')
        
        # Validate required fields
        if not all([title, description, starting_price, ends_at_str]):
            return JsonResponse({
                'error': 'Missing required fields: title, description, starting_price, ends_at'
            }, status=400)
        
        # Parse datetime
        from django.utils.dateparse import parse_datetime
        ends_at = parse_datetime(ends_at_str)
        if not ends_at:
            return JsonResponse({'error': 'Invalid date/time format'}, status=400)
        
        # Validate price
        try:
            starting_price_decimal = Decimal(starting_price)
            if starting_price_decimal <= 0:
                return JsonResponse({'error': 'Starting price must be greater than 0'}, status=400)
        except:
            return JsonResponse({'error': 'Invalid price format'}, status=400)
        
        # Create item (image_url is optional)
        item = Item.objects.create(
            owner=request.user,
            title=title,
            description=description,
            starting_price=starting_price_decimal,
            image_url=image_url,
            ends_at=ends_at,
        )
        
        # Handle image upload (primary)
        if image_file:
            item.image = image_file
            item.save()
            ItemImage.objects.create(item=item, image=image_file, is_primary=True)

        # Handle additional images
        extra_images = request.FILES.getlist('extra_images')
        for extra in extra_images:
            ItemImage.objects.create(item=item, image=extra, is_primary=False)
        
        # Get final image URL (prefer primary ItemImage)
        final_image_url = get_image_url(request, item)
        
        return JsonResponse({
            'id': item.id,
            'owner': item.owner.id,
            'owner_username': item.owner.username,
            'title': item.title,
            'description': item.description,
            'starting_price': str(item.starting_price),
            'current_price': str(item.current_price),
            'image_url': clean_url(final_image_url),
            'images': [
                clean_url(build_absolute_url(request, img.image.url))
                for img in item.images.all()
            ],
            'ends_at': item.ends_at.isoformat(),
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
        }, status=201)
        
    except Exception as e:
        print(f"ERROR creating item: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["PUT", "POST"])
def item_update(request: HttpRequest, item_id: int) -> JsonResponse:
    """Update an item (only by owner)."""
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    # Check if user is the owner
    if item.owner != request.user:
        return JsonResponse({'error': 'You do not have permission to edit this item'}, status=403)
    
    try:
        # Parse form data (works for both PUT and POST with FormData)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        ends_at_str = request.POST.get('ends_at', '').strip()
        image_file = request.FILES.get('image')
        
        # Debug logging
        print(f"DEBUG - Received data: title={title}, description={description}, ends_at={ends_at_str}")
        print(f"DEBUG - request.POST: {request.POST}")
        print(f"DEBUG - request.FILES: {request.FILES}")
        
        # Validate required fields
        if not all([title, description, ends_at_str]):
            return JsonResponse({
                'error': f'Missing required fields: title={bool(title)}, description={bool(description)}, ends_at={bool(ends_at_str)}'
            }, status=400)
        
        # Parse datetime
        from django.utils.dateparse import parse_datetime
        ends_at = parse_datetime(ends_at_str)
        if not ends_at:
            return JsonResponse({'error': 'Invalid date/time format'}, status=400)
        
        # Update item
        item.title = title
        item.description = description
        item.ends_at = ends_at
        
        # Handle new image upload (optional)
        if image_file:
            # Delete old image if exists
            if item.image:
                item.image.delete()
            # Set new primary image
            item.image = image_file
            # Update/create ItemImage record
            ItemImage.objects.filter(item=item, is_primary=True).delete()
            ItemImage.objects.create(item=item, image=image_file, is_primary=True)
        
        # Handle additional images if provided
        extra_images = request.FILES.getlist('extra_images')
        if extra_images:
            # Delete old extra images
            ItemImage.objects.filter(item=item, is_primary=False).delete()
            # Add new extra images
            for extra in extra_images:
                ItemImage.objects.create(item=item, image=extra, is_primary=False)
        
        item.save()
        
        # Get highest bid for current price
        highest_bid = item.bids.aggregate(max_bid=Max('amount')).get('max_bid')
        current_price = highest_bid if highest_bid else item.starting_price
        
        # Get final image URL (prefer primary ItemImage)
        final_image_url = get_image_url(request, item)
        images = [
            clean_url(build_absolute_url(request, img.image.url))
            for img in item.images.all()
        ]
        
        return JsonResponse({
            'id': item.id,
            'owner': item.owner.id,
            'owner_username': item.owner.username,
            'title': item.title,
            'description': item.description,
            'starting_price': str(item.starting_price),
            'current_price': str(current_price),
            'image_url': clean_url(final_image_url),
            'images': images,
            'ends_at': item.ends_at.isoformat(),
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
        })
    except Exception as e:
        print(f"ERROR updating item: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def item_delete(request: HttpRequest, item_id: int) -> JsonResponse:
    """Delete an item (only by owner)."""
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    # Check if user is the owner
    if item.owner != request.user:
        return JsonResponse({'error': 'You do not have permission to delete this item'}, status=403)
    
    try:
        # Delete associated image file if it exists
        if item.image:
            item.image.delete()
        
        item.delete()
        return JsonResponse({'success': True, 'message': 'Item deleted successfully'})
    except Exception as e:
        print(f"ERROR deleting item: {e}")
        import traceback
        traceback.print_exc()
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
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    bidder = request.user
    
    try:
        item = Item.objects.get(id=data['item_id'])
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    # Prevent seller from bidding on their own item
    if item.owner == bidder:
        return JsonResponse({'error': 'You cannot bid on your own item'}, status=400)
    
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


# === Item detail, Q&A, and helper endpoints ===

@require_http_methods(["GET"])
def item_detail(request: HttpRequest, item_id: int) -> JsonResponse:
    """Return single item with bids and Q&A."""
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

    try:
        # Highest bid for current price
        highest_bid = item.bids.aggregate(max_bid=Max('amount')).get('max_bid')
        current_price = highest_bid if highest_bid else item.starting_price

        bids_data = []
        for b in item.bids.order_by('-created_at'):
            bidder_profile, _ = Profile.objects.get_or_create(user=b.bidder)
            bidder_profile_image = ''
            if bidder_profile.profile_image:
                bidder_profile_image = build_absolute_url(request, bidder_profile.profile_image.url)
            
            bids_data.append({
                'id': b.id,
                'bidder': b.bidder.id,
                'bidder_name': b.bidder.username,
                'bidder_profile_image': clean_url(bidder_profile_image),
                'amount': str(b.amount),
                'created_at': b.created_at.isoformat(),
            })

        questions_data = []
        for q in item.questions.order_by('-created_at'):
            asker_profile, _ = Profile.objects.get_or_create(user=q.asker)
            asker_profile_image = ''
            if asker_profile.profile_image:
                asker_profile_image = build_absolute_url(request, asker_profile.profile_image.url)
            
            replies_data = []
            for r in q.replies.order_by('created_at'):
                author_profile, _ = Profile.objects.get_or_create(user=r.author)
                author_profile_image = ''
                if author_profile.profile_image:
                    author_profile_image = build_absolute_url(request, author_profile.profile_image.url)
                
                replies_data.append({
                    'id': r.id,
                    'author': r.author.id,
                    'author_name': r.author.username,
                    'author_profile_image': clean_url(author_profile_image),
                    'content': r.content,
                    'created_at': r.created_at.isoformat(),
                })
            
            questions_data.append({
                'id': q.id,
                'asker': q.asker.id,
                'asker_name': q.asker.username,
                'asker_profile_image': clean_url(asker_profile_image),
                'content': q.content,
                'created_at': q.created_at.isoformat(),
                'replies': replies_data,
            })

        # Images (prefer ItemImage primary)
        image_url = get_image_url(request, item)
        images = [
            clean_url(build_absolute_url(request, img.image.url))
            for img in item.images.all()
        ]

        # Get owner profile image
        owner_profile, _ = Profile.objects.get_or_create(user=item.owner)
        owner_profile_image = ''
        if owner_profile.profile_image:
            owner_profile_image = build_absolute_url(request, owner_profile.profile_image.url)

        return JsonResponse({
            'id': item.id,
            'owner': item.owner.id,
            'owner_username': item.owner.username,
            'owner_profile_image': clean_url(owner_profile_image),
            'title': item.title,
            'description': item.description,
            'starting_price': str(item.starting_price),
            'current_price': str(current_price),
            'image_url': clean_url(image_url),
            'images': images,
            'ends_at': item.ends_at.isoformat(),
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
            'bids': bids_data,
            'questions': questions_data,
        })
    
    except Exception as e:
        print(f"ERROR in item_detail: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def question_create(request: HttpRequest) -> JsonResponse:
    """Create a question for an item."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if 'item_id' not in data or not data.get('content'):
        return JsonResponse({'error': 'Missing item_id or content'}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    asker = request.user

    try:
        item = Item.objects.get(id=data['item_id'])
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

    # Prevent seller from asking a question on their own item
    if item.owner == asker:
        return JsonResponse({'error': 'You cannot ask a question on your own item'}, status=400)

    question = Question.objects.create(item=item, asker=asker, content=data['content'])
    return JsonResponse({
        'id': question.id,
        'item': item.id,
        'asker': asker.id,
        'content': question.content,
        'created_at': question.created_at.isoformat(),
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def reply_create(request: HttpRequest) -> JsonResponse:
    """Create a reply to a question."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if 'question_id' not in data or not data.get('content'):
        return JsonResponse({'error': 'Missing question_id or content'}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    author = request.user

    try:
        question = Question.objects.get(id=data['question_id'])
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    
    # Only the item owner can reply to questions on their item
    if question.item.owner != author:
        return JsonResponse({'error': 'Only the item owner can reply to questions'}, status=403)

    reply = Reply.objects.create(question=question, author=author, content=data['content'])
    return JsonResponse({
        'id': reply.id,
        'question': question.id,
        'author': author.id,
        'content': reply.content,
        'created_at': reply.created_at.isoformat(),
    }, status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
def item_delete(request: HttpRequest, item_id: int) -> JsonResponse:
    """Delete an item (only owner can delete)."""
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    if request.user != item.owner:
        return JsonResponse({'error': 'Only the owner can delete this item'}, status=403)

    item.delete()
    return JsonResponse({'success': True, 'message': 'Item deleted'}, status=200)


@csrf_exempt
@require_http_methods(["DELETE"])
def question_delete(request: HttpRequest, question_id: int) -> JsonResponse:
    """Delete a question (only asker can delete)."""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    if request.user != question.asker:
        return JsonResponse({'error': 'Only the asker can delete this question'}, status=403)

    question.delete()
    return JsonResponse({'success': True, 'message': 'Question deleted'}, status=200)


@csrf_exempt
@require_http_methods(["DELETE"])
def reply_delete(request: HttpRequest, reply_id: int) -> JsonResponse:
    """Delete a reply (only author can delete)."""
    try:
        reply = Reply.objects.get(id=reply_id)
    except Reply.DoesNotExist:
        return JsonResponse({'error': 'Reply not found'}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    if request.user != reply.author:
        return JsonResponse({'error': 'Only the author can delete this reply'}, status=403)

    reply.delete()
    return JsonResponse({'success': True, 'message': 'Reply deleted'}, status=200)


@csrf_exempt
@require_http_methods(["DELETE"])
def bid_delete(request: HttpRequest, bid_id: int) -> JsonResponse:
    """Delete a bid (only bidder can delete)."""
    try:
        bid = Bid.objects.get(id=bid_id)
    except Bid.DoesNotExist:
        return JsonResponse({'error': 'Bid not found'}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    if request.user != bid.bidder:
        return JsonResponse({'error': 'Only the bidder can delete this bid'}, status=403)

    bid.delete()
    return JsonResponse({'success': True, 'message': 'Bid deleted'}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def bid_update(request: HttpRequest, bid_id: int) -> JsonResponse:
    """Update a bid amount (only bidder can update)."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if 'amount' not in data:
        return JsonResponse({'error': 'Missing amount'}, status=400)

    try:
        bid = Bid.objects.get(id=bid_id)
    except Bid.DoesNotExist:
        return JsonResponse({'error': 'Bid not found'}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    if request.user != bid.bidder:
        return JsonResponse({'error': 'Only the bidder can update this bid'}, status=403)

    # Check auction hasn't ended
    if bid.item.ends_at < timezone.now():
        return JsonResponse({'error': 'Auction has ended'}, status=400)

    # Validate bid amount
    try:
        new_amount = Decimal(data['amount'])
        if new_amount <= 0:
            return JsonResponse({'error': 'Bid amount must be greater than 0'}, status=400)
    except:
        return JsonResponse({'error': 'Invalid amount format'}, status=400)

    # Check new amount is higher than current bid
    current_price = bid.item.current_price
    if new_amount <= current_price:
        return JsonResponse({
            'error': f'New bid must be greater than current price of {current_price}'
        }, status=400)

    # Update bid
    bid.amount = new_amount
    bid.save()

    return JsonResponse({
        'id': bid.id,
        'item': bid.item.id,
        'bidder': bid.bidder.id,
        'amount': str(bid.amount),
        'created_at': bid.created_at.isoformat(),
    }, status=200)
