"""
This module provides two annotated query sets:
Annotated books and annotated authors.
Both sets are used in search function.
Annotated books are also needed to order books by specific value
(such as average rating value of all reviews, number of reviews etc.)
"""

from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce, Concat

from book_review.models import Book, Author


def get_annotated_books(books_queryset):
    """
    Annotates Book model with 2 fields.
    Number of reviews and average rating of all reviews on this book.
    Both fields are used in sorting and displayed in book card and book details page.
    """
    num_reviews = Count('review__id')
    avg_rating = Coalesce(Avg('review__rating'), float(0))
    annotated_books_queryset = books_queryset.annotate(
        num_reviews=num_reviews,
        avg_rating=avg_rating
    )
    return annotated_books_queryset


def get_annotated_authors(authors_queryset):
    """
    Annotates Author model with 2 fields.
    Short name (first name and last name) and full name (first name, patronymic, last name)
    Both fields are used in search function.
    """
    author_full_name = Concat('first_name', Value(' '), 'patronymic', Value(' '), 'last_name')
    author_short_name = Concat('first_name', Value(' '), 'last_name')
    annotated_authors_queryset = authors_queryset.annotate(
        full_name=author_full_name,
        short_name=author_short_name
    )
    return annotated_authors_queryset


annotated_books = get_annotated_books(Book.objects.all())
annotated_authors = get_annotated_authors(Author.objects.all())
