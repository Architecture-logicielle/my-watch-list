from django.urls import path
from . import views

urlpatterns = [
    # Page principale : la watchlist
    path('', views.watchlist, name="watchlist"),

    # Actions TMDB
    path('add-netflix/', views.add_netflix_shows, name="add_netflix_shows"),
    path('add-prime/', views.add_prime_shows, name="add_prime_shows"),
    path('add-apple/', views.add_apple_shows, name="add_apple_shows"),

    # CRUD sur les séries
    path('update/<str:pk>/', views.update_show, name="update_show"),
    path('delete/<str:pk>/', views.delete_show, name="delete_show"),
]
