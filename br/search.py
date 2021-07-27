from django.db.models import Q
from .annotations import annotated_books, annotated_authors


def search(q, category):

    if category == 'book':
        results = annotated_books.filter(title__icontains=q)

    elif category == 'author':
        results = annotated_books.filter(
            Q(authors__in=annotated_authors.filter(full_name__icontains=q)) |
            Q(authors__in=annotated_authors.filter(short_name__icontains=q))
        )

    elif category == 'genre':
        results = annotated_books.filter(genres__name__icontains=q)

    elif category == 'year':
        results = annotated_books.filter(pub_date__year__iexact=q)

    elif category == 'any':
        results = annotated_books.filter(
            Q(title__icontains=q) |
            Q(authors__in=annotated_authors.filter(full_name__icontains=q)) |
            Q(authors__in=annotated_authors.filter(short_name__icontains=q)) |
            Q(genres__name__icontains=q) |
            Q(pub_date__year__icontains=q)
        )

    else:
        results = []

    if results:
        return results.order_by('-avg_rating', 'title')
    else:
        return []

