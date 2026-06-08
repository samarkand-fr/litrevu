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
    # 1. Guard Clause: Redirect authenticated users away from the signup page
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    # 2. Process form submission (POST request)
    if request.method == "POST":
        form = SignupForm(request.POST)
        # Validate form data and check password confirmation constraints
        if form.is_valid():
            # Persist the new user to the database
            user = form.save()
            # Authenticate and log the user in immediately after registration
            login(request, user)
            messages.success(request, "Bienvenue ! Votre compte a été créé.")
            # PRG Pattern: Redirect to prevent duplicate form submissions on refresh
            return redirect(settings.LOGIN_REDIRECT_URL)

    # 3. Handle GET request: Instantiate a blank registration form
    else:
        form = SignupForm()
    # Render the signup template with the form context
    return render(request, "authentication/signup.html", {"form": form})
