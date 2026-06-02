"""Models for the authentication application."""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model for the LitRevu project.

    Inherits from Django's AbstractUser to allow future customizations.
    """

    pass
