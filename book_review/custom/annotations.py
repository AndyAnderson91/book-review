from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce, Concat

from book_review.models import Book, Author


def get_annotated_books(books):
    """
    Annotates Book model with 2 fields.
    Number of reviews and average rating of all reviews on this book.
    Both fields are used in sorting and displayed in book card and book details page.
    """
    num_reviews = Count('review__id')
    avg_rating = Coalesce(Avg('review__rating'), float(0))
    annotated_books = books.annotate(
        num_reviews=num_reviews,
        avg_rating=avg_rating
    )
    return annotated_books


def get_annotated_authors(authors):
    """
    Annotates Author model with 2 fields.
    Short name (first name and last name) and full name (first name, patronymic, last name)
    Both fields are used in search function.
    """
    author_full_name = Concat('first_name', Value(' '), 'patronymic', Value(' '), 'last_name')
    author_short_name = Concat('first_name', Value(' '), 'last_name')
    annotated_authors = authors.annotate(
        full_name=author_full_name,
        short_name=author_short_name
    )
    return annotated_authors


BOOKS = get_annotated_books(Book.objects.all())
AUTHORS = get_annotated_authors(Author.objects.all())
