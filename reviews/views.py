"""Views for the reviews application.

This module handles all the core functionalities of the LitRevu platform,
including creating, updating, and deleting tickets and reviews. It also
manages the user activity feed and the subscription/follow system.
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FollowUserForm, ReviewForm, TicketForm
from .models import Review, Ticket, UserFollows

User = get_user_model()


@login_required
def ticket_create(request):
    """Handle creating a new Ticket.

    Renders the Ticket form, validates submissions, associates with the
    logged-in user, saves the Ticket, and redirects to the feed.
    """
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Le ticket a été créé avec succès.")
            return redirect("home")
    else:
        form = TicketForm()
    return render(
        request,
        "reviews/ticket_form.html",
        {"form": form, "title": "Créer un ticket"},
    )


@login_required
def ticket_update(request, ticket_id):
    """Handle editing an existing Ticket.

    Ensures the logged-in user is the author of the Ticket.
    Saves modifications and redirects to the user's posts list.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier ce ticket.")

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Le ticket a été modifié avec succès.")
            return redirect("posts_list")
    else:
        form = TicketForm(instance=ticket)
    return render(
        request,
        "reviews/ticket_form.html",
        {"form": form, "title": "Modifier votre ticket", "ticket": ticket},
    )


@login_required
def ticket_delete(request, ticket_id):
    """Handle deleting an existing Ticket.

    Ensures the logged-in user is the author.
    Renders confirmation page for GET and performs deletion on POST.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer ce ticket.")

    if request.method == "POST":
        ticket.delete()
        messages.success(request, "Le ticket a été supprimé.")
        return redirect("posts_list")

    return render(
        request,
        "reviews/confirm_delete.html",
        {
            "object_name": f"le ticket '{ticket.title}'",
            "cancel_url": "posts_list",
        },
    )


@login_required
def review_create_standalone(request):
    """Handle creating a review together with a new ticket.

    Renders forms for both Ticket and Review, validates and saves both,
    attaching the new Ticket to the Review, and redirects to the feed.
    """
    if request.method == "POST":
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            # Save ticket first to get an ID before linking it to the review
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            messages.success(
                request, "Le ticket et la critique ont été créés avec succès."
            )
            return redirect("home")
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()




@login_required
def review_create_response(request, ticket_id):
    """Handle writing a review in response to an existing Ticket.

    Saves the Review, links it to the specified Ticket, and redirects to the feed.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            messages.success(request, "Votre critique a été publiée.")
            return redirect("home")
    else:
        form = ReviewForm()
    return render(
        request,
        "reviews/review_response_form.html",
        {"form": form, "ticket": ticket},
    )


@login_required
def review_update(request, review_id):
    """Handle editing an existing Review.

    Ensures the logged-in user is the author of the Review.
    Saves modifications and redirects to the user's posts list.
    """
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier cette critique.")

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre critique a été modifiée avec succès.")
            return redirect("posts_list")
    else:
        form = ReviewForm(instance=review)
    return render(
        request,
        "reviews/review_form.html",
        {"form": form, "review": review, "ticket": review.ticket},
    )


@login_required
def review_delete(request, review_id):
    """Handle deleting an existing Review.

    Ensures the logged-in user is the author.
    Renders confirmation page for GET and performs deletion on POST.
    """
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer cette critique.")

    if request.method == "POST":
        review.delete()
        messages.success(request, "La critique a été supprimée.")
        return redirect("posts_list")

    return render(
        request,
        "reviews/confirm_delete.html",
        {
            "object_name": f"la critique '{review.headline}'",
            "cancel_url": "posts_list",
        },
    )


@login_required
def posts_list(request):
    """List all Tickets and Reviews created by the logged-in user.

    Combines them into a single sorted chronological list.
    """
    user_tickets = Ticket.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)

    posts = []

    # Pack tickets and reviews into uniform dictionaries for combined iteration
    for ticket in user_tickets:
        posts.append(
            {
                "type": "ticket",
                "instance": ticket,
                "time_created": ticket.time_created,
            }
        )
    for review in user_reviews:
        posts.append(
            {
                "type": "review",
                "instance": review,
                "time_created": review.time_created,
            }
        )

    # Sort the combined list by creation time (newest first)
    posts.sort(key=lambda x: x["time_created"], reverse=True)

    return render(request, "reviews/posts_list.html", {"posts": posts})


@login_required
def feed(request):
    """Render the activity feed for the logged-in user.

    Includes posts from followed users, from the user themselves, and reviews
    written in response to the user's tickets.
    """
    # Get the list of IDs that the current user follows
    followed_users = list(
        UserFollows.objects.filter(user=request.user).values_list(
            "followed_user", flat=True
        )
    )

    # Fetch tickets: belongs to user OR followed users
    tickets = Ticket.objects.filter(
        models.Q(user=request.user) | models.Q(user__in=followed_users)
    ).distinct()

    # Fetch reviews: belongs to user OR followed users OR replies to user's tickets
    reviews = Review.objects.filter(
        models.Q(user=request.user)
        | models.Q(user__in=followed_users)
        | models.Q(ticket__user=request.user)
    ).distinct()

    posts = []

    # Process tickets and check if current user has already replied to them
    for ticket in tickets:
        has_user_review = Review.objects.filter(
            ticket=ticket, user=request.user
        ).exists()
        posts.append(
            {
                "type": "ticket",
                "instance": ticket,
                "time_created": ticket.time_created,
                "has_user_review": has_user_review,
            }
        )

    for review in reviews:
        has_user_review = Review.objects.filter(
            ticket=review.ticket, user=request.user
        ).exists()
        posts.append(
            {
                "type": "review",
                "instance": review,
                "time_created": review.time_created,
                "has_user_review": has_user_review,
            }
        )

    # Chronological sort for the global feed (newest first)
    posts.sort(key=lambda x: x["time_created"], reverse=True)

    return render(request, "reviews/feed.html", {"posts": posts})


@login_required
def abonnements(request):
    """Handle displaying and managing follows/subscriptions.

    Supports subscribing to another user on POST, and displays following/followers lists.
    """
    if request.method == "POST":
        form = FollowUserForm(request.POST)
        if form.is_valid():
            username_to_follow = form.cleaned_data["username"]
            try:
                user_to_follow = User.objects.get(username=username_to_follow)

                # Validation checks before creating relation
                if user_to_follow == request.user:
                    messages.error(
                        request, "Vous ne pouvez pas vous abonner à vous-même."
                    )
                elif UserFollows.objects.filter(
                    user=request.user, followed_user=user_to_follow
                ).exists():
                    messages.error(request, f"Vous suivez déjà {username_to_follow}.")
                else:
                    UserFollows.objects.create(
                        user=request.user, followed_user=user_to_follow
                    )
                    messages.success(
                        request,
                        f"Vous êtes maintenant abonné à {username_to_follow}.",
                    )
                    return redirect("abonnements")
            except User.DoesNotExist:
                messages.error(request, "Cet utilisateur n'existe pas.")
    else:
        form = FollowUserForm()

    following = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)

    return render(
        request,
        "reviews/abonnements.html",
        {
            "form": form,
            "following": following,
            "followers": followers,
        },
    )


@login_required
def abonnement_delete(request, follow_id):
    """Handle unsubscribing/unfollowing a user.

    Ensures the user owns the UserFollows relationship, deletes it, and redirects.
    """
    follow = get_object_or_404(UserFollows, id=follow_id, user=request.user)
    followed_username = follow.followed_user.username
    if request.method == "POST":
        follow.delete()
        messages.success(request, f"Vous ne suivez plus {followed_username}.")
        return redirect("abonnements")

    return render(
        request,
        "reviews/confirm_delete.html",
        {
            "object_name": f"l'abonnement à {followed_username}",
            "cancel_url": "abonnements",
        },
    )
