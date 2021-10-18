from django.db.models import Q
from book_review.custom.annotations import annotated_books, annotated_authors


def search(q, category):
    """
    Return queryset of books by a given query. Books are sorted by average reviews rating and title.
    Categories are needed for cases if 'author', 'genre' or 'year' links are pressed.
    For example, if some books are published in 1984 year, and year link in book details page is pressed,
    only books with 1984 year publishing will be returned. G. Orwell '1984' titled book will not be in results.
    However, this system is only used while pressing links.
    If 1984 is entered in search bar, both - books with 1984 publishing year and Orwell's '1984' will be shown.
    For anything entered in search bar category is 'any'.
    This system allows user to filter search results.
    """

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
        results = annotated_books.filter(pub_date__year__icontains=q)

    elif category == 'any':
        results = annotated_books.filter(
            Q(title__icontains=q) |
            Q(authors__in=annotated_authors.filter(full_name__icontains=q)) |
            Q(authors__in=annotated_authors.filter(short_name__icontains=q)) |
            Q(genres__name__icontains=q) |
            Q(pub_date__year__icontains=q)
        )

    else:
        results = annotated_books.none()

    return results.order_by('-avg_rating', 'title')
