from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'book_review'
urlpatterns = [
    # Index page and list of anticipated books.
    path('', views.IndexListView.as_view(), name='index'),

    # List of published books ordered according to provided url argument.
    path('published_books/', views.BooksListView.as_view(), name='books_list'),

    # Book detail page.
    re_path(r'^book/(?P<pk>\d+)-(?P<slug>[\w-]+)/$', views.BookDetailView.as_view(), name='book'),

    # Create, edit and delete review pages.
    re_path(r'^review/(?P<pk>\d+)-(?P<slug>[\w-]+)/add/$', login_required(views.ReviewCreateView.as_view()), name='add_review'),
    re_path(r'^review/(?P<pk>\d+)-(?P<slug>[\w-]+)/edit/$', login_required(views.ReviewUpdateView.as_view()), name='edit_review'),
    re_path(r'^review/(?P<pk>\d+)-(?P<slug>[\w-]+)/delete/$', login_required(views.ReviewDeleteView.as_view()), name='delete_review'),

    # User reviews page.
    path('my_reviews/', login_required(views.MyReviewsListView.as_view()), name='my_reviews'),

    # Search results page.
    path('search/', views.SearchListView.as_view(), name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
