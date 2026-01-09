import os
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .forms import UserSignUpForm, UserLoginForm
from .models import Profile

def get_frontend_url():
    return os.getenv('FRONTEND_URL', 'http://localhost:5173')

def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})

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
@require_http_methods(["GET", "PUT"])
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

    try:
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()

        dob = request.POST.get("date_of_birth")
        profile.date_of_birth = dob or None

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
            "date_of_birth": profile.date_of_birth or "",
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