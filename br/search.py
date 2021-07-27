from django.db.models import Q
from .func_and_const import books


def search(q, category):

    if category == 'book':
        results = books.filter(title__icontains=q)

    elif category == 'author':
        results = books.filter(
            Q(author_full_name__icontains=q) |
            Q(author_short_name__icontains=q)
        )

    elif category == 'genre':
        results = books.filter(genres__name__icontains=q).distinct()

    elif category == 'year':
        results = books.filter(pub_date__year__iexact=q)

    elif category == 'any':
        results = books.filter(
            Q(title__icontains=q) |
            Q(author_full_name__icontains=q) |
            Q(author_short_name__icontains=q) |
            Q(genres__name__icontains=q) |
            Q(pub_date__year__icontains=q)
        )

    else:
        results = []

    return list(set(results))
