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
from django.urls import include, path
from . import views

urlpatterns = [
    # SPA
    path('', views.main_spa, name='main-spa'),
    
    # Auth endpoints (Emir's work)
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/profile/', views.profile, name='profile'),
    path('api/user/', views.user_info, name='user-info'),
    
    # Item & Bid endpoints (Krish's work)
    path('api/items/', views.item_list, name='item_list'),
    path('api/items/create/', views.item_create, name='item_create'),
    path('api/items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('api/items/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    path('api/bids/create/', views.bid_create, name='bid_create'),
    path('api/questions/create/', views.question_create, name='question_create'),
    path('api/replies/create/', views.reply_create, name='reply_create'),
]
