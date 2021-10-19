import datetime
from itertools import chain

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from django.http import Http404

from .models import Book, Review
from .custom.annotations import annotated_books
from .custom.search import search
from .forms import SearchForm
from .custom.constants import BOOKS_PER_PAGE, REVIEWS_PER_PAGE, SEARCH_CATEGORIES


class IndexListView(generic.list.ListView):
    """
    Return list of anticipated books ordered by book publication date and title.
    """
    template_name = 'general/index.html'
    context_object_name = 'anticipated_books'
    paginate_by = BOOKS_PER_PAGE

    def get_queryset(self):
        today = datetime.date.today()
        anticipated_books = annotated_books.filter(pub_date__gt=today)
        return anticipated_books.order_by('pub_date', 'title')


class BooksListView(generic.list.ListView):
    """
    Return list of published books ordered according to provided url argument.
    'recent', 'popular' or 'best_rated' argument values are possible.
    Different argument value leads to 404.
    """
    template_name = 'books/books_list.html'
    context_object_name = 'books'
    paginate_by = BOOKS_PER_PAGE

    def get(self, *args, **kwargs):
        if self.request.GET.get('order') is None:
            return redirect(reverse('book_review:books_list') + '?order=recent')
        return super().get(*args, **kwargs)

    def get_queryset(self):
        today = datetime.date.today()
        published_books = annotated_books.filter(pub_date__lte=today)
        order_dict = {
            'recent': '-pub_date',
            'popular': '-num_reviews',
            'best_rated': '-avg_rating',
        }
        order_key = self.request.GET.get('order')
        order_value = order_dict.get(order_key)
        if order_value is None:
            raise Http404
        return published_books.order_by(order_value, 'title')


class BookDetailView(generic.detail.DetailView):
    """
    Return a particular book and list of reviews for it.
    Reviews are ordered by review publication date.
    Authenticated user who already has review on requested book
    will always see his review on the top of the list regardless of the date.
    """
    model = Book
    queryset = annotated_books
    query_pk_and_slug = True
    template_name = 'books/book_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = Review.objects.filter(book=context.get('book')).order_by('-pub_date')
        user = self.request.user if self.request.user.is_authenticated else None
        user_review = reviews.filter(owner=user).first()

        if user_review:
            other_reviews = reviews.exclude(owner=user)
            reviews = list(chain((user_review, ), other_reviews))

        paginator = Paginator(reviews, REVIEWS_PER_PAGE)
        page_number = self.request.GET.get('page', '1')
        page_obj = paginator.get_page(page_number)

        context.update({
            'paginator': paginator,
            'page_obj': page_obj,
            'is_paginated': True,
            'reviews': reviews,
        })
        return context


class ReviewCreateView(generic.edit.CreateView):
    """
    Create new review on a book.
    User may have at most one review for each book.
    If user already has review for requested book or book is not published yet,
    user will be redirected to book detail page.
    """
    model = Review
    fields = ['rating', 'title', 'text']
    template_name = 'reviews/add_review.html'

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        book_reviews = book.review_set.all()
        users_already_reviewed = User.objects.filter(review__in=book_reviews)

        if not book.is_published() or request.user in users_already_reviewed:
            return redirect(book)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        context.update({
            'book': book,
        })
        return context

    def form_valid(self, form):
        new_review = form.save(commit=False)
        new_review.owner = self.request.user
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        new_review.book = book
        return super().form_valid(form)

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        return book.get_absolute_url()


class ReviewUpdateView(generic.edit.UpdateView):
    """
    Update authenticated user's review for a particular book.
    """
    fields = ['rating', 'title', 'text']
    template_name = 'reviews/edit_review.html'

    def get_object(self, queryset=None):
        # Get review by its book and owner fields since review.owner and review.book have unique_together constraint.
        # Benefit is a simple url without review id, for example, '/review/9-war-and-peace/edit/'.
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        review = get_object_or_404(Review, book=book, owner=self.request.user)
        return review

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        return book.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        context.update({
            'book': book
        })
        return context


class ReviewDeleteView(generic.edit.DeleteView):
    """
    Delete authenticated user's review for a particular book.
    """
    template_name = 'reviews/delete_review.html'
    query_pk_and_slug = True

    def get_object(self, queryset=None):
        # Get review by its book and owner fields since review.owner and review.book have unique_together constraint.
        # Benefit is a simple url without review id, for example, '/review/9-war-and-peace/delete/'.
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        review = get_object_or_404(Review, book=book, owner=self.request.user)
        return review

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        context.update({
            'book': book
        })
        return context

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        return book.get_absolute_url()


class MyReviewsListView(generic.list.ListView):
    """
    Return a list of all reviews written by a user.
    Reviews are ordered by review publication date.
    """
    template_name = 'reviews/my_reviews.html'
    context_object_name = 'my_reviews'
    paginate_by = REVIEWS_PER_PAGE

    def get_queryset(self):
        return Review.objects.filter(owner=self.request.user).order_by('-pub_date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SearchListView(generic.list.ListView):
    """
    Return a list of books found by request.
    'q' is a name of the variable that points to query string.
    """
    template_name = 'search/search.html'
    context_object_name = 'results'
    paginate_by = BOOKS_PER_PAGE

    def get(self, request, *args, **kwargs):
        form = SearchForm(data=request.GET)

        if form.is_valid():
            return super().get(request, *args, **kwargs)
        elif form.data.get('q') is None:
            return render(request, 'search/empty_search_request.html')
        else:
            return render(request, 'search/wrong_search_request.html')

    def get_queryset(self):
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        results = search(q, category)
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'q': self.request.GET.get('q'),
            'category': self.request.GET.get('category'),
            'SEARCH_CATEGORIES': SEARCH_CATEGORIES,
        })
        return context
