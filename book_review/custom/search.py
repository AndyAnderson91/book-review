from django.db.models import Q
from book_review.custom.annotations import BOOKS, AUTHORS


SEARCH_CATEGORIES = ['book', 'author', 'genre', 'year', 'any']


def search(q, category):
    """
    Categories are needed for cases if 'author', 'genre' or 'year' links are pressed.
    For example, if some books are published in 1984 year, and year link in book details page is pressed,
    only books with 1984 year publishing will be searched. G. Orwell '1984' titled book will not be in results.
    However, this system is only used while pressing links.
    If 1984 is entered in search bar, both - books with 1984 publishing year and Orwell's '1984' will be shown.
    For anything entered in search bar category is 'any'.
    'book' category is not actively using at the moment, but might be used in future.
    """

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

