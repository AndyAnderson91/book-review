from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'br'
urlpatterns = [
    # Main page
    path('', views.IndexListView.as_view(), name='index'),

    # Books list pages
    re_path(r'^(?P<sort_type>(recent|popular|best_rated))/$', views.BooksListView.as_view(), name='books_list'),

    # Book page
    re_path(r'^book/(?P<pk>\d+)-(?P<slug>[\w-]+)/$', views.BookDetailView.as_view(), name='book'),

    # Create, edit and delete review
    re_path(r'^review/(?P<pk>\d+)-(?P<slug>[\w-]+)/add/$', login_required(views.ReviewCreateView.as_view()), name='add_review'),
    re_path(r'^review/(?P<pk>\d+)-(?P<slug>[\w-]+)/edit/$', login_required(views.ReviewUpdateView.as_view()), name='edit_review'),
    re_path(r'^review/(?P<pk>\d+)-(?P<slug>[\w-]+)/delete/$', login_required(views.ReviewDeleteView.as_view()), name='delete_review'),

    # My reviews page
    path('my_reviews/', login_required(views.MyReviewsListView.as_view()), name='my_reviews'),

    # Search
    path('search/', views.SearchListView.as_view(), name='search'),
]
