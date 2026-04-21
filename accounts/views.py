from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
import re
from django.core.exceptions import ValidationError

def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    if not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one number.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValidationError("Password must contain at least one special character.")

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username","password1","password2")

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        validate_password_strength(password)
        return password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['username'].help_text = ""
        self.fields['password2'].label = "Confirm Password"

# Register View
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# Profile View
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')