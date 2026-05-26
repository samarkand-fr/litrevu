from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import models
from .models import Ticket, Review, UserFollows
from .forms import TicketForm, ReviewForm, FollowUserForm

User = get_user_model()


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Le ticket a été créé avec succès.")
            return redirect('home')
    else:
        form = TicketForm()
    return render(request, 'reviews/ticket_form.html', {'form': form, 'title': 'Créer un ticket'})


@login_required
def ticket_update(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier ce ticket.")

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Le ticket a été modifié avec succès.")
            return redirect('posts_list')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'reviews/ticket_form.html', {'form': form, 'title': 'Modifier votre ticket', 'ticket': ticket})


@login_required
def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer ce ticket.")

    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Le ticket a été supprimé.")
        return redirect('posts_list')

    return render(request, 'reviews/confirm_delete.html', {
        'object_name': f"le ticket '{ticket.title}'",
        'cancel_url': 'posts_list'
    })


@login_required
def review_create_standalone(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            messages.success(request, "Le ticket et la critique ont été créés avec succès.")
            return redirect('home')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()
    return render(request, 'reviews/review_standalone_form.html', {
        'ticket_form': ticket_form,
        'review_form': review_form
    })


@login_required
def review_create_response(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            messages.success(request, "Votre critique a été publiée.")
            return redirect('home')
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_response_form.html', {
        'form': form,
        'ticket': ticket
    })


@login_required
def review_update(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier cette critique.")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre critique a été modifiée avec succès.")
            return redirect('posts_list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/review_form.html', {
        'form': form,
        'review': review,
        'ticket': review.ticket
    })


@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer cette critique.")

    if request.method == 'POST':
        review.delete()
        messages.success(request, "La critique a été supprimée.")
        return redirect('posts_list')

    return render(request, 'reviews/confirm_delete.html', {
        'object_name': f"la critique '{review.headline}'",
        'cancel_url': 'posts_list'
    })


@login_required
def posts_list(request):
    user_tickets = Ticket.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)

    posts = []
    for ticket in user_tickets:
        posts.append({
            'type': 'ticket',
            'instance': ticket,
            'time_created': ticket.time_created
        })
    for review in user_reviews:
        posts.append({
            'type': 'review',
            'instance': review,
            'time_created': review.time_created
        })

    posts.sort(key=lambda x: x['time_created'], reverse=True)

    return render(request, 'reviews/posts_list.html', {'posts': posts})


@login_required
def feed(request):
    followed_users = list(UserFollows.objects.filter(user=request.user).values_list('followed_user', flat=True))

    tickets = Ticket.objects.filter(
        models.Q(user=request.user) | models.Q(user__in=followed_users)
    ).distinct()

    reviews = Review.objects.filter(
        models.Q(user=request.user) | models.Q(user__in=followed_users) | models.Q(ticket__user=request.user)
    ).distinct()

    posts = []
    for ticket in tickets:
        has_user_review = Review.objects.filter(ticket=ticket, user=request.user).exists()
        posts.append({
            'type': 'ticket',
            'instance': ticket,
            'time_created': ticket.time_created,
            'has_user_review': has_user_review
        })
    for review in reviews:
        has_user_review = Review.objects.filter(ticket=review.ticket, user=request.user).exists()
        posts.append({
            'type': 'review',
            'instance': review,
            'time_created': review.time_created,
            'has_user_review': has_user_review
        })

    posts.sort(key=lambda x: x['time_created'], reverse=True)

    return render(request, 'reviews/feed.html', {'posts': posts})


@login_required
def abonnements(request):
    if request.method == 'POST':
        form = FollowUserForm(request.POST)
        if form.is_valid():
            username_to_follow = form.cleaned_data['username']
            try:
                user_to_follow = User.objects.get(username=username_to_follow)
                if user_to_follow == request.user:
                    messages.error(request, "Vous ne pouvez pas vous abonner à vous-même.")
                elif UserFollows.objects.filter(user=request.user, followed_user=user_to_follow).exists():
                    messages.error(request, f"Vous suivez déjà {username_to_follow}.")
                else:
                    UserFollows.objects.create(user=request.user, followed_user=user_to_follow)
                    messages.success(request, f"Vous êtes maintenant abonné à {username_to_follow}.")
                    return redirect('abonnements')
            except User.DoesNotExist:
                messages.error(request, "Cet utilisateur n'existe pas.")
    else:
        form = FollowUserForm()

    following = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)

    return render(request, 'reviews/abonnements.html', {
        'form': form,
        'following': following,
        'followers': followers,
    })


@login_required
def abonnement_delete(request, follow_id):
    follow = get_object_or_404(UserFollows, id=follow_id, user=request.user)
    followed_username = follow.followed_user.username
    if request.method == 'POST':
        follow.delete()
        messages.success(request, f"Vous ne suivez plus {followed_username}.")
        return redirect('abonnements')

    return render(request, 'reviews/confirm_delete.html', {
        'object_name': f"l'abonnement à {followed_username}",
        'cancel_url': 'abonnements'
    })
