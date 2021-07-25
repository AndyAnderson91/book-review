from django.db.models import Value as V
from django.db.models.functions import Concat
from .models import Book, Author

def search(q, category):
    books = Book.objects.all()
    if category == 'author':
        results = search_by_author(q, books)
    elif category == 'genre':
        results = search_by_genre(q, books)
    elif category == 'year':
        results = search_by_year(q, books)
    elif category is None:
        results = []
    else:
        results = []
    return results


def search_by_genre(q, books):
    return books.filter(genres__name__icontains=q)


def search_by_year(q, books):
    return books.filter(pub_date__year__icontains=q)


def search_by_author(q, books):
    return books.annotate(full_name=Concat('authors__first_name', V(' '), 'authors__patronymic', V(' '), 'authors__last_name')).filter(full_name__icontains=q)


def search_by_book_title(q, books):
    return books.filter(title__icontains=q)
