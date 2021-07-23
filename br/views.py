import datetime

from django.views import generic
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from .models import Author, Genre, Book, Review
from .forms import SimpleForm


class SimpleFormView(generic.edit.FormView):
    template_name = 'br/simple_form.html'
    form_class = SimpleForm
    success_url = '/simple_form/'

    def get(self, request, *args, **kwargs):
        print(self.request.GET)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        print(self.request.POST)
        print(form.cleaned_data)

        return super().form_valid(form)


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

        book_reviews = Review.objects.filter(book=book).order_by('-pub_date')

        if self.request.user.is_authenticated and book_reviews.filter(owner=self.request.user):
            my_review = book_reviews.get(owner=self.request.user)
            other_reviews = book_reviews.exclude(owner=self.request.user)
        else:
            my_review = None
            other_reviews = book_reviews

        context['my_review'] = my_review
        context['other_reviews'] = other_reviews
        context['authors'] = authors
        return context


class ReviewCreateView(generic.edit.CreateView):
    model = Review
    fields = ['rating', 'title', 'text']
    template_name = 'br/add_review.html'
    query_pk_and_slug = True

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        return book.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.kwargs)
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        context['book'] = book
        return context

    def form_valid(self, form):
        new_review = form.save(commit=False)
        new_review.owner = self.request.user
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        new_review.book = book
        return super().form_valid(form)
