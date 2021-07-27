from django.db.models import Value as V, Avg, Count
from django.db.models.functions import Concat, Coalesce
from .models import Book

def annotated_books():
    author_full_name = Concat('authors__first_name', V(' '), 'authors__patronymic', V(' '), 'authors__last_name')
    author_short_name = Concat('authors__first_name', V(' '), 'authors__last_name')
    books = Book.objects.annotate(author_full_name=author_full_name,  num_reviews=Count('review__id'), avg_rating=Coalesce(Avg('review__rating'), float(0)))
    return books


books = annotated_books()