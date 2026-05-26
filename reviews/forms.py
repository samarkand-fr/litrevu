from django import forms
from .models import Ticket, Review


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'image': 'Image',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'id': 'id_description'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'id_image'}),
        }


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        label="Note",
        coerce=int,
        choices=[(i, f"- {i}") for i in range(6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-radio-input'}),
    )

    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
        labels = {
            'headline': 'Titre',
            'body': 'Commentaire',
        }
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_headline'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'id': 'id_body'}),
        }


class FollowUserForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur",
            'id': 'id_username'
        })
    )
