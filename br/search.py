from operator import attrgetter

from django.db.models import Q, Value as V
from django.db.models.functions import Concat
from .models import Book

search_categories = ['book', 'author', 'genre', 'year']


def search(q, category):
    full_name = Concat('authors__first_name', V(' '), 'authors__patronymic', V(' '), 'authors__last_name')
    short_name = Concat('authors__first_name', V(' '), 'authors__last_name')
    books = Book.objects.annotate(full_name=full_name, short_name=short_name)

    if category == 'book':
        results = books.filter(title__icontains=q)

    elif category == 'author':
        results = books.filter(
            Q(full_name__icontains=q) |
            Q(short_name__icontains=q)
        )

    elif category == 'genre':
        results = books.filter(genres__name__icontains=q).distinct()

    elif category == 'year':
        results = books.filter(pub_date__year__iexact=q)

    elif category is None:
        results = books.filter(
            Q(title__icontains=q) |
            Q(full_name__icontains=q) |
            Q(short_name__icontains=q) |
            Q(genres__name__icontains=q) |
            Q(pub_date__year__icontains=q)
        )

    else:
        results = []

    return list(set(results))


def split_results(results):
    anticipated = []
    published = []
    if results:
        for book in results:
            if book.is_published():
                published.append(book)
            else:
                anticipated.append(book)
    published = sorted(published, key=attrgetter('pub_date'), reverse=True)
    anticipated = sorted(anticipated, key=attrgetter('pub_date'), reverse=True)
    return published, anticipated
