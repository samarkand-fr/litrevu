"""Views for the authentication application."""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from django.contrib import messages
from .forms import SignupForm


def signup_page(request):
    """Handle user registration.

    If a logged-in user accesses this page, they are redirected to the homepage.
    Otherwise, handles form validation, user creation, automatic login, and redirects
    to the post-login destination.
    """
    # 1. Redirect if already logged in
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 2. Automatic login after registration
            login(request, user)
            messages.success(request, "Bienvenue ! Votre compte a été créé.")
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignupForm()
    return render(request, "authentication/signup.html", {"form": form})
