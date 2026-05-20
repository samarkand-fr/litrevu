from django.urls import path
from . import views

urlpatterns = [
    path('ticket/add/', views.ticket_create, name='ticket_create'),
    path('ticket/<int:ticket_id>/modifier/', views.ticket_update, name='ticket_update'),
    path('ticket/<int:ticket_id>/supprimer/', views.ticket_delete, name='ticket_delete'),

    path('review/add/', views.review_create_standalone, name='review_create'),
    path('ticket/<int:ticket_id>/review/add/', views.review_create_response, name='review_create_response'),
    path('review/<int:review_id>/modifier/', views.review_update, name='review_update'),
    path('review/<int:review_id>/supprimer/', views.review_delete, name='review_delete'),
    path('posts/', views.posts_list, name='posts_list'),
    path('home/', views.feed, name='home'),
]
