"""
Forms for user authentication and profile management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile


class RegisterForm(UserCreationForm):
    """User registration form with email."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    """User login form."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class ProfileForm(forms.ModelForm):
    """Profile update form with logo URL."""
    class Meta:
        model = Profile
        fields = ('theme', 'accent_color', 'logo_url')
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'accent_color': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color'
            }),
            'logo_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://example.com/logo.png'
            })
        }