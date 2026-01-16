"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path, path
from . import views

urlpatterns = [
    # SPA
    path('', views.main_spa, name='main-spa'),
    
    # Auth endpoints 
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('api/profile/', views.profile, name='profile'),
    path('api/user/', views.user_info, name='user-info'),
    path('api/users/<int:user_id>/', views.user_profile_display, name='user-profile-display'),
    
    # Item & Bid endpoints 
    path('api/items/create/', views.item_create, name='item-create'),
    path('api/items/', views.item_list, name='item-list'),
    path('api/items/<int:item_id>/', views.item_detail, name='item-detail'),
    path('api/items/<int:item_id>/delete/', views.item_delete, name='item-delete'),
    path('api/bids/create/', views.bid_create, name='bid-create'),
    path('api/bids/<int:bid_id>/delete/', views.bid_delete, name='bid-delete'),
    
    # Q&A endpoints
    path('api/questions/create/', views.question_create, name='question-create'),
    path('api/questions/<int:question_id>/delete/', views.question_delete, name='question-delete'),
    path('api/replies/create/', views.reply_create, name='reply-create'),
    path('api/replies/<int:reply_id>/delete/', views.reply_delete, name='reply-delete'),
]
