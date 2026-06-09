"""Views for the reviews application.

This module handles all the core functionalities of the LitRevu platform,
including creating, updating, and deleting tickets and reviews. It also
manages the user activity feed and the subscription/follow system.
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FollowUserForm, ReviewForm, TicketForm
from .models import Review, Ticket, UserFollows

# Fetch the active user model for the project
User = get_user_model()


@login_required
def ticket_create(request):
    """Handle creating a new Ticket.

    Renders the Ticket form, validates submissions, associates with the
    logged-in user, saves the Ticket, and redirects to the feed.
    """
    if request.method == "POST":
        # Bind the form with submitted POST data and files (like images)
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            # commit=False prevents immediate saving to the database
            # so we can assign the logged-in user first
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Le ticket a été créé avec succès.")
            return redirect("home")
    else:
        # Empty form for a GET request to render the creation page
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
    # Fetch the ticket or raise a 404 error if not found
    ticket = get_object_or_404(Ticket, id=ticket_id)
    # Security: Verify that the logged-in user is the actual author of the ticket
    if ticket.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier ce ticket.")

    if request.method == "POST":
        # Pass the existing instance to update it instead of creating a new database row
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Le ticket a été modifié avec succès.")
            return redirect("posts_list")
    else:
        # Pre-populate the form with the current ticket data for a GET request
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

    # Security: Only the author can delete their own ticket
    if ticket.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer ce ticket.")

    if request.method == "POST":
        # Perform the actual deletion after confirmation
        ticket.delete()
        messages.success(request, "Le ticket a été supprimé.")
        return redirect("posts_list")

    # For a GET request, render a deletion confirmation page
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
        # Validate both forms simultaneously
        if ticket_form.is_valid() and review_form.is_valid():
            # 1. Save the ticket first to generate its ID in the database
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            # 2. Save the review and link it to the newly created ticket
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            messages.success(
                request, "Le ticket et la critique ont été créés avec succès."
            )
            return redirect("home")
    else:
        # Initialize two empty forms for the initial render
        ticket_form = TicketForm()
        review_form = ReviewForm()
    return render(
        request,
        "reviews/review_standalone_form.html",
        {"ticket_form": ticket_form, "review_form": review_form},
    )


@login_required
def review_create_response(request, ticket_id):
    """Handle writing a review in response to an existing Ticket.

    Saves the Review, links it to the specified Ticket, and redirects to the feed.
    """
    # Identify the ticket the user is responding to  based on the provided  ticket_id and ensure it exists, otherwise return a 404 error
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Link the review to the existing ticket and the logged-in user
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
    # Security: Only the review author can edit it
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
    # Security: Only the author can delete their review
    if review.user != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à supprimer cette critique.")

    if request.method == "POST":
        review.delete()
        messages.success(request, "La critique a été supprimée.")
        return redirect("posts_list")
    # Render confirmation page before deletion
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
    # Separately fetch the user's tickets and reviews
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
    # Store the currently logged-in user instance in a local variable
    user = request.user

    # 1. RETRIEVE FOLLOWED USERS
    # Fetch only the IDs of the users the current user follows.
    followed_users = UserFollows.objects.filter(user=user).values_list(
        "followed_user", flat=True
    )

    # 2. Fetch tickets and prefetch related user data for the feed,
    # filtering for tickets by the user and followed users in one query
    # .select_related("user") performs an SQL JOIN to prefetch author data for each ticket
    tickets = (
        Ticket.objects.filter(Q(user=user) | Q(user__in=followed_users))
        .select_related("user")
        .distinct()
    )

    # 3. FETCH REVIEWS (CRITIQUES)
    # Fetch reviews written by the user, their follows, OR written by anyone in response to the user's tickets.
    # .select_related prefetches the review author, the connected ticket, and the ticket's author in one shot.
    reviews = (
        Review.objects.filter(
            Q(user=user) | Q(user__in=followed_users) | Q(ticket__user=user)
        )
        .select_related("user", "ticket", "ticket__user")
        .distinct()
    )

    # 4.Fetch the IDs of all tickets the logged-in user has already reviewed in a SINGLE database hit.
    reviewed_ticket_ids = set(
        Review.objects.filter(user=user).values_list("ticket_id", flat=True)
    )
    # Initialize the unified list that will hold all combined feed items (Tickets + Reviews)
    posts = []

    # 5. BUILD UNIFIED STREAM (DATA FUSION)
    # Loop through the retrieved tickets and standardize them into clean dictionary structures
    for ticket in tickets:
        posts.append(
            {
                "type": "ticket",
                "instance": ticket,
                "time_created": ticket.time_created,
                # Ultra-fast lookup in memory using the set created in Step 4 to determine if the user has already reviewed this ticket
                "has_user_review": ticket.id in reviewed_ticket_ids,
            }
        )
    # Process and append reviews into the exact same global list
    for review in reviews:
        posts.append(
            {
                "type": "review",
                "instance": review,
                "time_created": review.time_created,
                "has_user_review": review.ticket_id in reviewed_ticket_ids,
            }
        )

    # 6. GLOBAL CHRONOLOGICAL SORTING
    # Sort the combined list of different objects based on their creation timestamp.
    # reverse=True ensures a reverse-chronological order (newest posts appear first).
    posts.sort(key=lambda x: x["time_created"], reverse=True)

    # 7. FINAL RENDERING
    # Pass the unified, perfectly sorted feed list to the 'reviews/feed.html' template
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
                # Business rule 1: Users cannot follow themselves
                if user_to_follow == request.user:
                    messages.error(
                        request, "Vous ne pouvez pas vous abonner à vous-même."
                    )
                    # Business rule 2: Prevent duplicate follow relationships
                elif UserFollows.objects.filter(
                    user=request.user, followed_user=user_to_follow
                ).exists():
                    messages.error(request, f"Vous suivez déjà {username_to_follow}.")
                else:
                    # Create the follow relationship
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
    # Fetch following (users I follow) and followers (users following me)
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
    # Fetch the specific follow relationship belonging strictly to the current user based on the provided follow_id, or return a 404 if not found
    follow = get_object_or_404(UserFollows, id=follow_id, user=request.user)
    followed_username = follow.followed_user.username
    if request.method == "POST":
        # Delete the follow relationship
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
