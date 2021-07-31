from django.db.models import Q
from br.custom.annotations import BOOKS, AUTHORS


SEARCH_CATEGORIES = ['book', 'author', 'genre', 'year', 'any']


def search(q, category):

    if category == 'book':
        results = BOOKS.filter(title__icontains=q)

    elif category == 'author':
        results = BOOKS.filter(
            Q(authors__in=AUTHORS.filter(full_name__icontains=q)) |
            Q(authors__in=AUTHORS.filter(short_name__icontains=q))
        )

    elif category == 'genre':
        results = BOOKS.filter(genres__name__icontains=q)

    elif category == 'year':
        results = BOOKS.filter(pub_date__year__icontains=q)

    elif category == 'any':
        results = BOOKS.filter(
            Q(title__icontains=q) |
            Q(authors__in=AUTHORS.filter(full_name__icontains=q)) |
            Q(authors__in=AUTHORS.filter(short_name__icontains=q)) |
            Q(genres__name__icontains=q) |
            Q(pub_date__year__icontains=q)
        )

    else:
        results = BOOKS.none()

    return results.order_by('-avg_rating', 'title')

