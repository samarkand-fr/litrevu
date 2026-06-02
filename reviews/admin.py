"""Admin configuration for the reviews application.

This module registers the Ticket, Review, and UserFollows models with the
Django admin site, customizing their list displays, search capabilities,
and filters.
"""

from django.contrib import admin
from .models import Ticket, Review, UserFollows


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin interface configuration for Ticket objects."""

    list_display = ("title", "user", "time_created")
    search_fields = ("title", "user__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface configuration for Review objects."""

    list_display = ("headline", "ticket", "user", "rating", "time_created")
    list_filter = ("rating", "time_created")
    search_fields = ("headline", "user__username", "ticket__title")


@admin.register(UserFollows)
class UserFollowsAdmin(admin.ModelAdmin):
    """Admin interface configuration for UserFollows relationships."""

    list_display = ("user", "followed_user")
    search_fields = ("user__username", "followed_user__username")
