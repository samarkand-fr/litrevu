from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from django.contrib import messages
from .forms import SignupForm

def signup_page(request):
    # 1. Redirection si déjà connecté
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 2. Connexion automatique après inscription
            login(request, user)
            messages.success(request, "Bienvenue ! Votre compte a été créé.")
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignupForm()
    return render(request, 'authentication/signup.html', {'form': form})

def home(request):
    # Temporary home page to redirect to after login
    return render(request, 'base.html', {'message': 'Bienvenue sur la page d\'accueil !'})