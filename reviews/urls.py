"""URL routing for the reviews application."""

from django.urls import path
from . import views

urlpatterns = [
    # 1. Homepage: Serves the activity feed for the authenticated user
    path("", views.feed, name="home"),
    # Tickets
    # Route for creating a standalone ticket
    path("ticket/add/", views.ticket_create, name="ticket_create"),
    # Route for editing an existing ticket
    path("ticket/<int:ticket_id>/modifier/", views.ticket_update, name="ticket_update"),
    # Route for deleting an existing ticket
    path(
        "ticket/<int:ticket_id>/supprimer/", views.ticket_delete, name="ticket_delete"
    ),
    # Reviews
    # Route for creating a combined ticket + review in one form
    path("review/add/", views.review_create_standalone, name="review_create"),
    # Route for creating a review in response to a specific existing ticket
    path(
        "ticket/<int:ticket_id>/review/add/",
        views.review_create_response,
        name="review_create_response",
    ),
    # Route for editing an existing review
    path("review/<int:review_id>/modifier/", views.review_update, name="review_update"),
    # Route for deleting an existing review
    path(
        "review/<int:review_id>/supprimer/", views.review_delete, name="review_delete"
    ),
    # My Space & Subscriptions
    # Lists only the user's own tickets and reviews (the "Vos posts" section)
    path("posts/", views.posts_list, name="posts_list"),
    # Management page to follow other users
    path("abonnements/", views.abonnements, name="abonnements"),
    # Route to unfollow a specific user
    path(
        "abonnements/<int:follow_id>/supprimer/",
        views.abonnement_delete,
        name="abonnement_delete",
    ),
]
