from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'br'
urlpatterns = [

    # Four pages in Navbar
    path('', views.IndexListView.as_view(), name='index'),
    path('recent/', views.RecentListView.as_view(), name='recent'),
    path('popular/', views.PopularListView.as_view(), name='popular'),
    path('ratings/', views.RatingListView.as_view(), name='ratings'),

    # Book page
    path('book/<int:pk>-<slug:slug>/', views.BookDetailView.as_view(), name='book'),

    # Create, edit, delete review
    path('review/<int:pk>-<slug:slug>/add/', login_required(views.ReviewCreateView.as_view()), name='add_review'),
    path('review/<int:pk>-<slug:slug>/edit/', login_required(views.ReviewUpdateView.as_view()), name='edit_review'),
    path('review/<int:pk>-<slug:slug>/delete/', login_required(views.ReviewDeleteView.as_view()), name='delete_review'),

    # Search
    path('search/', views.SearchListView.as_view(), name='search'),

]
