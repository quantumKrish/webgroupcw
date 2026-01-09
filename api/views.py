from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .forms import UserSignUpForm, UserLoginForm
from .models import Profile
import os

def get_frontend_url():
    """Helper to get frontend URL from environment or default"""
    return os.getenv('FRONTEND_URL', 'http://localhost:3000')

def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})

@require_http_methods(["GET", "POST"])
def signup(request: HttpRequest):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile automatically
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('http://localhost:5173')
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
                return redirect('http://localhost:5173')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, 'api/login.html', {'form': form})

@require_http_methods(["GET"])
def logout_view(request: HttpRequest):
    logout(request)
    return redirect('http://localhost:5173')

@login_required
@require_http_methods(["GET", "PUT"])
def profile(request: HttpRequest):
    """Get or update user profile"""
    user = request.user
    
    # Create profile if it doesn't exist
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'GET':
        profile_image_url = None
        if profile.profile_image:
            profile_image_url = profile.profile_image.url
        
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_of_birth': profile.date_of_birth or '',
            'profile_image_url': profile_image_url,
        })
    
    elif request.method == 'PUT':
        try:
            # Update User model fields
            user.email = request.POST.get('email', user.email)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.save()
            
            # Update Profile model fields
            date_of_birth = request.POST.get('date_of_birth')
            if date_of_birth:
                profile.date_of_birth = date_of_birth
            
            if 'profile_image' in request.FILES:
                # Delete old image if exists
                if profile.profile_image:
                    profile.profile_image.delete()
                profile.profile_image = request.FILES['profile_image']
            
            profile.save()
            
            profile_image_url = None
            if profile.profile_image:
                profile_image_url = profile.profile_image.url
            
            return JsonResponse({
                'success': True,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_of_birth': profile.date_of_birth or '',
                'profile_image_url': profile_image_url,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def user_info(request: HttpRequest):
    """Return current user info for auth check"""
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    })