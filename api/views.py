import os
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Max
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings 
from decimal import Decimal
import json
from typing import Any

from .forms import UserSignUpForm, UserLoginForm
from .models import Profile, Item, Bid, Question, Reply

def get_frontend_url():
    return os.getenv('FRONTEND_URL', 'http://localhost:5173')

def get_image_url(request: HttpRequest, item: Item) -> str:
    """Build absolute URL for item image."""
    if item.image:
        return request.build_absolute_uri(item.image.url)
    elif item.image_url:
        return item.image_url
    return ''

def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})

def send_winner_email(
    to_email: str,
    item_title: str
) -> None:
    subject = "🎉 You won the auction!"
    message = f"Congratulations! You won the auction for '{item_title}'."

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
        profile_image_url = request.build_absolute_uri(profile.profile_image.url) if profile.profile_image else None
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

        profile_image_url = request.build_absolute_uri(profile.profile_image.url) if profile.profile_image else None
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
    profile, _ = Profile.objects.get_or_create(user=user)
    profile_image_url = request.build_absolute_uri(profile.profile_image.url) if profile.profile_image else None
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'profile_image_url': profile_image_url,
        'authenticated': True,
    })


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
                # Get image URL - only use image_url since image field doesn't exist
                image_url = ''
                if item.image:
                    image_url = request.build_absolute_uri(item.image.url)
                elif item.image_url:
                    image_url = item.image_url

                
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
                    'image_url': image_url,
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
        
        # Handle image upload
        if image_file:
            item.image = image_file
            item.save()
        
        # Get final image URL
        final_image_url = ''
        if item.image:
            final_image_url = request.build_absolute_uri(item.image.url)
        elif item.image_url:
            final_image_url = item.image_url
        
        return JsonResponse({
            'id': item.id,
            'owner': item.owner.id,
            'owner_username': item.owner.username,
            'title': item.title,
            'description': item.description,
            'starting_price': str(item.starting_price),
            'current_price': str(item.current_price),
            'image_url': final_image_url,
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

        bids_data = [
            {
                'id': b.id,
                'bidder': b.bidder.id,
                'bidder_name': b.bidder.username,
                'amount': str(b.amount),
                'created_at': b.created_at.isoformat(),
            }
            for b in item.bids.order_by('-created_at')
        ]

        questions_data = []
        for q in item.questions.order_by('-created_at'):
            questions_data.append({
                'id': q.id,
                'asker': q.asker.id,
                'asker_name': q.asker.username,
                'text': q.text,  # Changed from 'content' to 'text'
                'created_at': q.created_at.isoformat(),
                'replies': [
                    {
                        'id': r.id,
                        'responder': r.responder.id,  # Changed from 'author' to 'responder'
                        'responder_name': r.responder.username,
                        'text': r.text,  # Changed from 'content' to 'text'
                        'created_at': r.created_at.isoformat(),
                    }
                    for r in q.replies.order_by('created_at')
                ],
            })

        # Get image URL - only use image_url field
        image_url = ''
        if item.image:
            image_url = request.build_absolute_uri(item.image.url)
        elif item.image_url:
            image_url = item.image_url

        return JsonResponse({
            'id': item.id,
            'owner': item.owner.id,
            'owner_username': item.owner.username,
            'title': item.title,
            'description': item.description,
            'starting_price': str(item.starting_price),
            'current_price': str(current_price),
            'image_url': image_url,
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
