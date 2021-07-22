import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.db.models import Avg, Count

from django.contrib.auth.models import User
from .models import Author, Genre, Book, Review


class IndexListView(generic.list.ListView):
    template_name = 'br/index.html'
    context_object_name = 'anticipated_books'

    def get_queryset(self):
        return Book.objects.filter(pub_date__gt=datetime.date.today()).order_by('-pub_date')


class RecentListView(generic.list.ListView):
    template_name = 'br/recent.html'
    context_object_name = 'recent_books'

    def get_queryset(self):
        books = Book.objects.filter(pub_date__lte=datetime.date.today())
        return books.annotate(num_reviews=Count('review'), avg_rating=Avg('review__rating')).order_by('-pub_date')


class PopularListView(generic.list.ListView):
    template_name = 'br/popular.html'
    context_object_name = 'popular_books'

    def get_queryset(self):
        books = Book.objects.filter(pub_date__lte=datetime.date.today())
        return books.annotate(num_reviews=Count('review'), avg_rating=Avg('review__rating')).order_by('-num_reviews')


class RatingTemplateView(generic.base.TemplateView):
    template_name = 'br/rating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.filter(pub_date__lte=datetime.date.today())
        best_rated_books = books.annotate(num_reviews=Count('review'), avg_rating=Avg('review__rating')).order_by('-avg_rating')
        context['best_rated_books'] = best_rated_books
        return context


class SearchTemplateView(generic.base.TemplateView):
    template_name = 'br/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # search algoritms and adding results to context
        return context


class BookDetailView(generic.detail.DetailView):
    model = Book
    query_pk_and_slug = True
    template_name = 'br/book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = context['book']
        authors = book.authors.all()
        context['authors'] = authors
        return context
