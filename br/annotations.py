from django.db.models import Avg, Count, Value as V
from django.db.models.functions import Coalesce, Concat

from .models import Book, Author


def get_annotated_books():
    num_reviews = Count('review__id')
    avg_rating = Coalesce(Avg('review__rating'), float(0))
    books = Book.objects.annotate(
        num_reviews=num_reviews,
        avg_rating=avg_rating
    )
    return books


def get_annotated_authors():
    author_full_name = Concat('first_name', V(' '), 'patronymic', V(' '), 'last_name')
    author_short_name = Concat('first_name', V(' '), 'last_name')
    authors = Author.objects.annotate(
        full_name=author_full_name,
        short_name=author_short_name
    )
    return authors


annotated_books = get_annotated_books()
annotated_authors = get_annotated_authors()