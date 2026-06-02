"""URL routing for the reviews application."""

from django.urls import path
from . import views

urlpatterns = [
    # 1. Homepage
    path("", views.feed, name="home"),
    # Tickets
    path("ticket/add/", views.ticket_create, name="ticket_create"),
    path("ticket/<int:ticket_id>/modifier/", views.ticket_update, name="ticket_update"),
    path(
        "ticket/<int:ticket_id>/supprimer/", views.ticket_delete, name="ticket_delete"
    ),
    # Reviews
    path("review/add/", views.review_create_standalone, name="review_create"),
    path(
        "ticket/<int:ticket_id>/review/add/",
        views.review_create_response,
        name="review_create_response",
    ),
    path("review/<int:review_id>/modifier/", views.review_update, name="review_update"),
    path(
        "review/<int:review_id>/supprimer/", views.review_delete, name="review_delete"
    ),
    # My Space & Subscriptions
    path("posts/", views.posts_list, name="posts_list"),
    path("abonnements/", views.abonnements, name="abonnements"),
    path(
        "abonnements/<int:follow_id>/supprimer/",
        views.abonnement_delete,
        name="abonnement_delete",
    ),
]
