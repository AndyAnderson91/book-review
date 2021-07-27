from django.db.models import Q, Value as V, Avg, Count
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

    elif category == 'any':
        results = books.filter(
            Q(title__icontains=q) |
            Q(full_name__icontains=q) |
            Q(short_name__icontains=q) |
            Q(genres__name__icontains=q) |
            Q(pub_date__year__icontains=q)
        )

    else:
        results = []

    if results:
        results = add_annotations(results)

    return list(set(results))


def add_annotations(books_set):
    return books_set.annotate(num_reviews=Count('review'), avg_rating=Avg('review__rating'))

