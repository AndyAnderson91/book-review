import datetime

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from .models import Book, Review
from br.custom.annotations import BOOKS
from br.custom.search import SEARCH_CATEGORIES, search
from .forms import SearchForm


BOOKS_PER_PAGE = 2
REVIEWS_PER_PAGE = 5


class IndexListView(generic.list.ListView):
    template_name = 'br/index.html'
    context_object_name = 'anticipated_books'
    paginate_by = BOOKS_PER_PAGE

    def get_queryset(self):
        today = datetime.date.today()
        anticipated_books = BOOKS.filter(pub_date__gt=today)
        return anticipated_books.order_by('pub_date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cur_page = context.get('page_obj').number
        page_range = context.get('paginator').get_elided_page_range(cur_page, on_each_side=2, on_ends=1)

        context.update({
            'page_range': page_range,
        })

        return context


class BooksListView(generic.list.ListView):
    template_name = 'br/books_list.html'
    context_object_name = 'books'
    paginate_by = BOOKS_PER_PAGE

    def get_queryset(self):
        today = datetime.date.today()
        published_books = BOOKS.filter(pub_date__lte=today)
        sort_type = self.kwargs.get('sort_type')
        sort_by = {
            'recent': '-pub_date',
            'popular': '-num_reviews',
            'best_rated': '-avg_rating',
        }
        return published_books.order_by(
            sort_by.get(sort_type, '-pub_date'),
            'title'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cur_page = context.get('page_obj').number
        page_range = context.get('paginator').get_elided_page_range(cur_page, on_each_side=2, on_ends=1)

        context.update({
            'sort_type': self.kwargs.get('sort_type'),
            'page_range': page_range,
        })

        return context


class BookDetailView(generic.detail.DetailView):
    model = Book
    queryset = BOOKS
    query_pk_and_slug = True
    template_name = 'br/book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reviews = Review.objects.filter(book=context.get('book')).order_by('-pub_date')
        if self.request.user.is_authenticated and reviews.filter(owner=self.request.user):
            my_review = [reviews.get(owner=self.request.user), ]
            other_reviews = list(reviews.exclude(owner=self.request.user))
        else:
            my_review = list()
            other_reviews = list(reviews)

        reviews = my_review + other_reviews
        paginator = Paginator(reviews, REVIEWS_PER_PAGE)

        cur_page = self.request.GET.get('page')
        page_obj = paginator.get_page(cur_page)
        page_range = paginator.get_elided_page_range(cur_page, on_each_side=2, on_ends=1)

        context.update({
            'paginator': paginator,
            'page_obj': page_obj,
            'page_range': page_range,
            'reviews': reviews,
        })

        return context


class ReviewCreateView(generic.edit.CreateView):
    model = Review
    fields = ['rating', 'title', 'text']
    template_name = 'br/add_review.html'

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
    fields = ['rating', 'title', 'text']
    template_name = 'br/edit_review.html'

    def get_object(self, queryset=None):
        """
        There is db constraint on review.owner and review.book as unique_together, so its safe to get review this way.
        """
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
    template_name = 'br/delete_review.html'
    query_pk_and_slug = True

    def get_object(self, queryset=None):
        """
        There is db constraint on review.owner and review.book as unique_together, so its safe to get review this way.
        """
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
    template_name = 'br/my_reviews.html'
    context_object_name = 'my_reviews'
    paginate_by = REVIEWS_PER_PAGE

    def get_queryset(self):
        return Review.objects.filter(owner=self.request.user).order_by('-pub_date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cur_page = context.get('page_obj').number
        page_range = context.get('paginator').get_elided_page_range(cur_page, on_each_side=2, on_ends=1)

        context.update({
            'page_range': page_range,
        })

        return context


class SearchListView(generic.list.ListView):
    template_name = 'br/search.html'
    context_object_name = 'results'
    paginate_by = BOOKS_PER_PAGE

    def get(self, request, *args, **kwargs):
        form = SearchForm(data=request.GET)

        if form.is_valid():
            return super().get(request, *args, **kwargs)
        elif not form.data.get('q'):
            return render(request, 'br/empty_search_request.html')
        else:
            return render(request, 'br/wrong_search_request.html')

    def get_queryset(self):
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        results = search(q, category)
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cur_page = context.get('page_obj').number
        page_range = context.get('paginator').get_elided_page_range(cur_page, on_each_side=2, on_ends=1)

        context.update({
            'page_range': page_range,
            'q': self.request.GET.get('q'),
            'category': self.request.GET.get('category'),
            'SEARCH_CATEGORIES': SEARCH_CATEGORIES,
        })
        return context
