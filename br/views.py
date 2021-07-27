import datetime
from operator import attrgetter

from django.views import generic
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Book, Review
from .search import search_categories, search, add_annotations


# class BooksListView(generic.list.ListView):
#     model = Book
#     template_name = 'br/books_list.html'
#     context_object_name = 'books'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print(self.request.path)
#         return super


class IndexListView(generic.list.ListView):
    template_name = 'br/index.html'
    context_object_name = 'anticipated_books'

    def get_queryset(self):
        all_books = Book.objects.all()
        anticipated_books = get_anticipated(all_books)
        return anticipated_books.order_by('pub_date', 'title')


class RecentListView(generic.list.ListView):
    template_name = 'br/recent.html'
    context_object_name = 'recent_books'
    paginate_by = 10

    def get_queryset(self):
        all_books = Book.objects.all()
        published_books = get_published(all_books)
        annotated_books = add_annotations(published_books)
        return annotated_books.order_by('-pub_date', 'title')


class PopularListView(generic.list.ListView):
    template_name = 'br/popular.html'
    context_object_name = 'popular_books'
    paginate_by = 10

    def get_queryset(self):
        all_books = Book.objects.all()
        published_books = get_published(all_books)
        annotated_books = add_annotations(published_books)
        return annotated_books.order_by('-num_reviews', 'title')


class RatingListView(generic.list.ListView):
    template_name = 'br/rating.html'
    context_object_name = 'best_rated_books'
    paginate_by = 10

    def get_queryset(self):
        all_books = Book.objects.all()
        published_books = get_published(all_books)
        annotated_books = add_annotations(published_books)
        return annotated_books.order_by('-avg_rating', 'title')


class BookDetailView(generic.detail.DetailView):
    model = Book
    query_pk_and_slug = True
    template_name = 'br/book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reviews = Review.objects.filter(book=context['book']).order_by('-pub_date')
        print(self.request.user)

        if self.request.user.is_authenticated and reviews.filter(owner=self.request.user):
            my_review = reviews.get(owner=self.request.user)
            other_reviews = reviews.exclude(owner=self.request.user)
        else:
            my_review = None
            other_reviews = reviews

        context['my_review'] = my_review
        context['other_reviews'] = other_reviews
        return context


class ReviewCreateView(generic.edit.CreateView):
    model = Review
    fields = ['rating', 'title', 'text']
    template_name = 'br/add_review.html'

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        book_reviews = book.review_set.all()
        users_already_reviewed = User.objects.filter(review__in=book_reviews)
        if not book.is_published() or request.user in users_already_reviewed:
            return redirect(book)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        context['book'] = book
        return context

    def form_valid(self, form):
        new_review = form.save(commit=False)
        new_review.owner = self.request.user
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        new_review.book = book
        return super().form_valid(form)

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        return book.get_absolute_url()


class ReviewUpdateView(generic.edit.UpdateView):
    fields = ['rating', 'title', 'text']
    template_name = 'br/edit_review.html'

    def get_object(self, queryset=None):
        """
        There is db constraint on review.owner and review.book as unique_together, so its safe to get review this way.
        """
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        review = get_object_or_404(Review, book=book, owner=self.request.user)
        return review

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        return book.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        context['book'] = book
        return context


class ReviewDeleteView(generic.edit.DeleteView):
    template_name = 'br/delete_review.html'
    query_pk_and_slug = True

    def get_object(self, queryset=None):
        """
        There is db constraint on review.owner and review.book as unique_together, so its safe to get review this way.
        """
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        review = get_object_or_404(Review, book=book, owner=self.request.user)
        return review

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        context['book'] = book
        return context

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        return book.get_absolute_url()


class SearchListView(generic.list.ListView):
    template_name = 'br/search.html'
    context_object_name = 'results'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        print(self.request.GET)
        if not self.request.GET.get('q'):
            return redirect('br:index')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        q = self.request.GET['q']
        category = self.request.GET.get('category')
        results = search(q, category)
        return sorted(results, key=attrgetter('pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = context['results']
        published = count_published(results)

        context.update({
            'q': self.request.GET['q'],
            'category': self.request.GET.get('category'),
            'available_categories': search_categories,
            'published': published,
        })

        return context


def get_published(books_set):
    today = datetime.date.today()
    return books_set.filter(pub_date__lte=today)


def get_anticipated(books_set):
    today = datetime.date.today()
    return books_set.filter(pub_date__gt=today)


def count_published(results):
    published = 0
    for book in results:
        if book.is_published():
            published += 1
    return published
