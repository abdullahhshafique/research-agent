# apps/accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Max
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required

from .forms import RegisterForm, LoginForm, ProfileForm

User = get_user_model()


def home_view(request):
    """Home/landing page."""
    return render(request, 'pages/home.html')


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('accounts:home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:home')
    else:
        form = RegisterForm()
    
    return render(request, 'pages/accounts/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('accounts:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'accounts:home')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'pages/accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:home')


@login_required
def profile_view(request):
    """User profile management."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'pages/accounts/profile.html', {'form': form})