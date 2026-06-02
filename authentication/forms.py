"""Forms for the authentication application."""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    """Custom registration form extending Django's UserCreationForm.

    Ensures new users are created using the active custom user model.
    """

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username",)
