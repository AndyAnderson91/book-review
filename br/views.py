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
REVIEWS_PER_PAGE = 2


class IndexListView(generic.list.ListView):
    """
    Home page. Contains greeting and anticipated books list.
    """
    template_name = 'br/index.html'
    context_object_name = 'anticipated_books'
    paginate_by = BOOKS_PER_PAGE

    def get_queryset(self):
        """
        Sends anticipated books list ordered by book pub_date and title.
        """
        today = datetime.date.today()
        anticipated_books = BOOKS.filter(pub_date__gt=today)
        return anticipated_books.order_by('pub_date', 'title')


class BooksListView(generic.list.ListView):
    """
    Responsible for 3 pages (recent, popular and best rated books).
    Sends list of published books ordered by requested type.
    """
    template_name = 'br/books_list.html'
    context_object_name = 'books'
    paginate_by = BOOKS_PER_PAGE

    def get_queryset(self):
        today = datetime.date.today()
        published_books = BOOKS.filter(pub_date__lte=today)
        # Gets sorting type value from request.
        # Might be one of 'recent', 'popular' or 'best_rated'.
        sort_type = self.kwargs.get('sort_type')
        # Matches it with an ordering field.
        sort_by = {
            'recent': '-pub_date',
            'popular': '-num_reviews',
            'best_rated': '-avg_rating',
        }
        # Returns published books ordered according to the request.
        return published_books.order_by(
            sort_by.get(sort_type, '-pub_date'),
            'title'
        )

    def get_context_data(self, **kwargs):
        """
        Adds sort type to context to display it in page title.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'sort_type': self.kwargs.get('sort_type')
            })

        return context


class BookDetailView(generic.detail.DetailView):
    """
    Sends particular book and reviews list on it.
    """
    model = Book
    queryset = BOOKS
    query_pk_and_slug = True
    template_name = 'br/book_details.html'

    def get_context_data(self, **kwargs):
        """
        Reviews are sorted by review pub_date field.
        If authenticated user requests book detail page and he has review on this book,
        he will always see his review first regardless of the date.
        """
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

        context.update({
            'paginator': paginator,
            'page_obj': page_obj,
            'reviews': reviews,
        })

        return context


class ReviewCreateView(generic.edit.CreateView):
    model = Review
    fields = ['rating', 'title', 'text']
    template_name = 'br/add_review.html'

    def get(self, request, *args, **kwargs):
        """
        Each user may have maximum 1 review on each book,
        so authenticated user already did it, he will be redirected.
        Also only published books can be reviewed.
        """
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        book_reviews = book.review_set.all()
        users_already_reviewed = User.objects.filter(review__in=book_reviews)

        if not book.is_published() or request.user in users_already_reviewed:
            return redirect(book)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Book is added to context to display it's title in page.
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        context.update({
            'book': book,
        })
        return context

    def form_valid(self, form):
        new_review = form.save(commit=False)
        # Adds values to hidden Review form fields: owner and book.
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
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        # There is db constraint on review.owner and review.book as unique_together, so its safe to get review this way.
        # Benefit is an url that looks same for every user. For example, '/review/9-war-and-peace/edit/'
        review = get_object_or_404(Review, book=book, owner=self.request.user)
        return review

    def get_success_url(self):
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        return book.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Sends book to template to show it's title on the page.
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        context.update({
            'book': book
        })
        return context


class ReviewDeleteView(generic.edit.DeleteView):
    template_name = 'br/delete_review.html'
    query_pk_and_slug = True

    def get_object(self, queryset=None):
        book = get_object_or_404(Book, id=self.kwargs.get('pk'), slug=self.kwargs.get('slug'))
        # Same as in ReviewUpdateView. Allows to have same url for any user on review delete page for particular book.
        # For example, '/review/9-war-and-peace/delete/'
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
    Sends reviews filtered by user.
    """
    template_name = 'br/my_reviews.html'
    context_object_name = 'my_reviews'
    paginate_by = REVIEWS_PER_PAGE

    def get_queryset(self):
        return Review.objects.filter(owner=self.request.user).order_by('-pub_date', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
            # Displays empty request page.
            return render(request, 'br/empty_search_request.html')
        else:
            # Displays wrong request page.
            return render(request, 'br/wrong_search_request.html')

    def get_queryset(self):
        # 'q' is a search request.
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
