import datetime
from random import randrange

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from br.models import Author, Book, Genre, Review
from br.views import BOOKS_PER_PAGE, REVIEWS_PER_PAGE
from django.utils.text import slugify


def create_books(n, published):
    """
    n - amount of books to create,
    published - boolean variable. True if published books are needed, False otherwise.
    """
    books = []
    # direction = -1 means timedelta will lower date.today(), +1 will increase.
    direction = -1 if published else 1

    for book_number in range(n):
        books.append(Book.objects.create(
            title='book №{0}'.format(book_number+1),
            slug=slugify('book №{0}'.format(book_number+1)),
            pub_date=datetime.date.today() + direction * datetime.timedelta(days=(book_number+1))
        ))
    return books


def create_reviews(books, user, n=1):
    """
    n - amount of reviews to create,
    owner = user, book = book.
    """
    reviews = []
    for review_number in range(n):
        reviews.append(Review.objects.create(
            rating=randrange(1, 6),
            title='review №{0}'.format(review_number+1),
            text='review №{0} text'.format(review_number+1),
            book=books[review_number],
            owner=user
        ))
    return reviews


class IndexListViewTest(TestCase):
    """
    Class for testing IndexListView.
    Only anticipated books should be sent to template.
    """

    @classmethod
    def setUpTestData(cls):
        # Creates 14 published books to make sure they are not sent to template
        cls.published_books = create_books(14, published=True)

    def test_index_view_url_accessible_by_name(self):
        """
        Tests reverse using view name.
        """
        response = self.client.get(reverse('br:index'))
        self.assertEqual(response.status_code, 200)

    def test_no_anticipated_books_message(self):
        """
        If no anticipated books, an appropriate message is displayed.
        """
        response = self.client.get(reverse('br:index'))
        self.assertContains(response, 'No books are anticipated at the moment')

    def test_no_anticipated_books_queryset(self):
        """
        If no anticipated books, queryset sent to template is empty.
        """
        response = self.client.get(reverse('br:index'))
        self.assertQuerysetEqual(response.context['anticipated_books'], [])

    def test_anticipated_books_sent_to_template(self):
        """
        If anticipated books exist, they are sent to template.
        """
        # Creating 32 anticipated books.
        create_books(32, published=False)
        response = self.client.get(reverse('br:index'))
        self.assertTrue(response.context['anticipated_books'])

    def test_anticipated_books_pagination_on(self):
        # Creating 32 anticipated books.
        create_books(32, published=False)
        response = self.client.get(reverse('br:index'))
        self.assertTrue(response.context['is_paginated'])

    def test_anticipated_books_per_page(self):
        # Creating 32 anticipated books.
        anticipated_books = create_books(32, published=False)
        response = self.client.get(reverse('br:index'))
        if len(anticipated_books) >= BOOKS_PER_PAGE:
            self.assertEqual(len(response.context['page_obj']), BOOKS_PER_PAGE)
        else:
            self.assertEqual(len(response.context['page_obj']), len(anticipated_books))

    def test_anticipated_books_count_sent_to_template(self):
        # Creating 32 anticipated books.
        anticipated_books = create_books(32, published=False)
        response = self.client.get(reverse('br:index'))
        self.assertEqual(response.context['paginator'].count, len(anticipated_books))


class BooksListViewTest(TestCase):
    """
    Class for testing BooksListView
    This view is used by 3 urls: /recent/, /popular/, /best_rated/
    Each url defines sorting type of published books.
    Only published books can be displayed.
    """

    @classmethod
    def setUpTestData(cls):
        # Creates 27 published books to make sure they are not sent to template.
        cls.anticipated_books = create_books(27, published=False)

    def test_books_list_view_accessible_by_name(self):
        for arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(arg,)))
            self.assertEqual(response.status_code, 200)

    def test_no_published_books_message(self):
        """
        If no published books, an appropriate message is displayed.
        """
        for arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(arg,)))
            self.assertContains(response, 'No published books are added to site')

    def test_no_published_books_empty_queryset(self):
        """
        If no published books, an empty set is sent to template.
        """
        for arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(arg,)))
            self.assertQuerysetEqual(response.context['books'], [])

    def test_published_books_pagination_on(self):
        # Creating 49 published books.
        create_books(49, published=True)

        for url_arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(url_arg,)))
            self.assertTrue(response.context['is_paginated'])

    def test_published_books_sent_to_template_count(self):
        # Creating 49 published books.
        published_books = create_books(49, published=True)

        for url_arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(url_arg,)))
            self.assertEqual(response.context['paginator'].count, len(published_books))

    def test_published_books_per_page(self):
        # Creating 49 published books.
        published_books = create_books(49, published=True)

        for url_arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(url_arg,)))
            if len(published_books) >= BOOKS_PER_PAGE:
                self.assertEqual(len(response.context['page_obj']), BOOKS_PER_PAGE)
            else:
                self.assertEqual(len(response.context['page_obj']), len(published_books))


class BookDetailViewTest(TestCase):
    """
    Class for testing BookDetailView.
    Every book is accessible with query_pk_and_slug = True
    Only published books may have reviews.
    If book has reviews, they're displayed on book detail page.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Creating 1 published and 1 anticipated books
        """
        cls.published_book = create_books(1, published=True)[0]
        cls.anticipated_book = create_books(1, published=False)[0]
        cls.user = User.objects.create_user(username='andy', password='1')

        cls.books = [cls.published_book, cls.anticipated_book]

    def test_book_url_accessible_by_name(self):
        for book in self.books:
            response = self.client.get(book.get_absolute_url())
            self.assertEqual(response.status_code, 200)

    def test_book_context_sent_to_template(self):
        for book in self.books:
            response = self.client.get(book.get_absolute_url())
            self.assertEqual(response.context['book'], book)

    def test_published_book_with_no_reviews_message(self):
        """
        If no reviews on a published book, an appropriate message is displayed.
        """
        response = self.client.get(self.published_book.get_absolute_url())
        self.assertContains(response, 'No reviews yet')

    def test_published_book_with_no_reviews_queryset(self):
        """
        If no reviews on a published book, an empty queryset is sent to template.
        """
        response = self.client.get(self.published_book.get_absolute_url())
        self.assertEqual(response.context['reviews'], [])

    def test_published_book_with_review(self):
        """
        Tests book detail page with review.
        """
        review = create_reviews([self.published_book], self.user)[0]
        response = self.client.get(self.published_book.get_absolute_url())
        self.assertEqual(response.context['reviews'], [review])

    def test_anticipated_book_message(self):
        """
        Anticipated book can't be reviewed.
        So there is an appropriate message on review section of book detail page.
        """
        response = self.client.get(self.anticipated_book.get_absolute_url())
        self.assertContains(response, 'Reviews can be written as soon as the book is published')

    def test_anticipated_book_reviews_queryset(self):
        response = self.client.get(self.anticipated_book.get_absolute_url())
        self.assertEqual(response.context['reviews'], [])


class ReviewCreateViewTest(TestCase):
    """
    Class for testing ReviewCreateView.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Creating book and user.
        """
        cls.book = create_books(1, published=True)[0]
        cls.user = User.objects.create_user(username='andy', password='1')
        cls.write_review_url = reverse('br:add_review', kwargs={
            'pk': cls.book.id,
            'slug': cls.book.slug
        })
        cls.new_review_data = {
            'rating': '5',
            'title': 'review_title1',
            'text': 'review_text1',
            'book': cls.book,
            'owner': cls.user
        }

    def test_non_authenticated_user_redirect(self):
        """
        Non authenticated users should be redirected to login page with 'next' parameter,
        """
        response = self.client.get(self.write_review_url)
        self.assertEqual(response.status_code, 302)

    def test_non_authenticated_user_redirect_url(self):
        response = self.client.get(self.write_review_url)
        self.assertEqual(response['location'], '{0}?next=/review{1}add/'.format(
            reverse('users:login')[:-1],
            self.book.get_absolute_url()[5:])
                         )

    def test_authenticated_user_with_no_review_get(self):
        """
        Authenticated user has access to write review page unless he already reviewed this book.
        """
        # Log user in.
        self.client.force_login(self.user)
        response = self.client.get(self.write_review_url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_with_no_review_post(self):
        """
        Authenticated user can write review on a book unless he already did it.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Posting data in CreateView built-in form.
        self.client.post(self.write_review_url, self.new_review_data)
        # Check review is created.
        reviews = Review.objects.all()
        self.assertEqual(len(reviews), 1)

    def test_authenticated_user_with_no_review_redirect_after_post(self):
        """
        After review is added user is redirected to book page.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Posting data in CreateView built-in form.
        response = self.client.post(self.write_review_url, self.new_review_data)
        # Check redirect.
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_redirect_if_attempts_to_add_second_review(self):
        """
        User can't have more than one review per book.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Creating first review.
        create_reviews([self.book], self.user)
        # If user will try to get write review page again he will be redirected.
        response = self.client.get(self.write_review_url)
        self.assertEqual(response.status_code, 302)


class ReviewUpdateViewTest(TestCase):
    """
    Class for testing ReviewUpdateView.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Creating book and user.
        """
        cls.book = create_books(1, published=True)[0]
        cls.user = User.objects.create_user(username='andy', password='1')
        cls.update_review_url = reverse('br:edit_review', kwargs={
            'pk': cls.book.id,
            'slug': cls.book.slug
        })
        cls.review_update_data = {
            'rating': '5',
            'title': 'updated_review_title',
            'text': 'updated_review_text',
            'book': cls.book,
            'owner': cls.user
        }

    def test_non_authenticated_user_redirect(self):
        """
        Non authenticated users should be redirected to login page with 'next' parameter,
        """
        response = self.client.get(self.update_review_url)
        self.assertEqual(response.status_code, 302)

    def test_non_authenticated_user_redirect_url(self):
        response = self.client.get(self.update_review_url)
        self.assertEqual(response['location'], '{0}?next=/review{1}edit/'.format(
            reverse('users:login')[:-1],
            self.book.get_absolute_url()[5:])
                         )

    def test_authenticated_user_with_no_review_get(self):
        """
        Authenticated user who doesn't have review on a particular book will get 404 if he'll try to get edit page via url.
        """
        # Log user in.
        self.client.force_login(self.user)
        response = self.client.get(self.update_review_url)
        self.assertEqual(response.status_code, 404)

    def test_authenticated_user_with_review_get(self):
        """
        Authenticated user with review on a particular book can edit it.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Creating review with standard data.
        create_reviews([self.book], self.user)
        # Get edit review page.
        response = self.client.get(self.update_review_url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_with_review_post(self):
        # Log user in.
        self.client.force_login(self.user)
        # Creating review with standard data.
        create_reviews([self.book], self.user)
        # Posts new data to update review.
        self.client.post(self.update_review_url, self.review_update_data)
        # Tests if review was updated.
        self.assertEqual(Review.objects.first().title, self.review_update_data['title'])

    def test_authenticated_user_with_review_post_redirect(self):
        # Log user in.
        self.client.force_login(self.user)
        # Creating review with standard data.
        create_reviews([self.book], self.user)
        # Posts new data to update review.
        response = self.client.post(self.update_review_url, self.review_update_data)
        # Redirect to book page after review update.
        self.assertEqual(response.status_code, 302)


class ReviewDeleteViewTest(TestCase):
    """
    Class for testing ReviewDeleteView.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Creating book and user.
        """
        cls.book = create_books(1, published=True)[0]
        cls.user = User.objects.create_user(username='andy', password='1')
        cls.delete_review_url = reverse('br:delete_review', kwargs={
            'pk': cls.book.id,
            'slug': cls.book.slug
        })

    def test_non_authenticated_user_redirect(self):
        """
        Non authenticated users should be redirected to login page with 'next' parameter,
        """
        response = self.client.get(self.delete_review_url)
        self.assertEqual(response.status_code, 302)

    def test_non_authenticated_user_redirect_url(self):
        response = self.client.get(self.delete_review_url)
        self.assertEqual(response['location'], '{0}?next=/review{1}delete/'.format(
            reverse('users:login')[:-1],
            self.book.get_absolute_url()[5:])
                         )

    def test_authenticated_user_with_no_review_get(self):
        """
        Authenticated user who doesn't have review on a particular book will get 404 if he'll try to get delete page via url.
        """
        # Log user in.
        self.client.force_login(self.user)
        response = self.client.get(self.delete_review_url)
        self.assertEqual(response.status_code, 404)

    def test_authenticated_user_with_review_get(self):
        """
        Authenticated user with review can have access to confirm delete page.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Creating review.
        create_reviews([self.book], self.user)
        response = self.client.get(self.delete_review_url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_with_review_get_message(self):
        """
        Authenticated user with review can have access to confirm delete page.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Creating review.
        create_reviews([self.book], self.user)
        response = self.client.get(self.delete_review_url)
        self.assertContains(response, 'Are you sure you want to delete review on «{0}»?'.format(self.book.title))

    def test_authenticated_user_with_no_review_post(self):
        """
        Authenticated user without review on a particular book will get 404 if he'll try to get delete page via url.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Attempts to delete non-existing review.
        response = self.client.post(self.delete_review_url)
        self.assertEqual(response.status_code, 404)

    def test_authenticated_user_with_review_post(self):
        """
        Authenticated user with review on a particular book can delete it.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Creating review.
        create_reviews([self.book], self.user)
        # Posts updated data to created review.
        self.client.post(self.delete_review_url)
        # Redirect to book page after review update.
        self.assertEqual(len(self.book.review_set.all()), 0)


class MyReviewListViewTest(TestCase):
    """
    Class for testing MyReviewListView.
    This view is needed to display all user's reviews.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Creating 39 books and 1 user.
        """
        cls.books = create_books(39, published=True)
        cls.user = User.objects.create_user(username='andy', password='1')
        cls.my_reviews_url = reverse('br:my_reviews')

    def test_non_authenticated_user_redirect(self):
        """
        Non authenticated users should be redirected to login page with 'next' parameter,
        """
        response = self.client.get(self.my_reviews_url)
        self.assertEqual(response.status_code, 302)

    def test_non_authenticated_user_redirect_url(self):
        response = self.client.get(self.my_reviews_url)
        self.assertEqual(response['location'], '{0}?next=/my_reviews/'.format(
            reverse('users:login')[:-1])
                         )

    def test_authenticated_user_get(self):
        """
        Authenticated user has access to read, edit and delete his reviews.
        """
        # Log user in.
        self.client.force_login(self.user)
        response = self.client.get(self.my_reviews_url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_with_no_reviews_message(self):
        # Log user in.
        self.client.force_login(self.user)
        response = self.client.get(self.my_reviews_url)
        self.assertContains(response, 'No written reviews yet')

    def test_authenticated_user_with_no_reviews_queryset(self):
        # Log user in.
        self.client.force_login(self.user)
        response = self.client.get(self.my_reviews_url)
        self.assertQuerysetEqual(response.context['my_reviews'], [])

    def test_pagination_on(self):
        # Log user in.
        self.client.force_login(self.user)
        # Creates 18 reviews
        reviews = create_reviews(self.books, self.user, n=18)
        response = self.client.get(self.my_reviews_url)
        self.assertTrue(response.context['is_paginated'])

    def test_reviews_per_page(self):
        # Log user in.
        self.client.force_login(self.user)
        # Creating 27 reviews.
        reviews = create_reviews(self.books, self.user, n=27)
        response = self.client.get(self.my_reviews_url)
        if len(reviews) >= REVIEWS_PER_PAGE:
            self.assertEqual(len(response.context['page_obj']), REVIEWS_PER_PAGE)
        else:
            self.assertEqual(len(response.context['page_obj']), len(reviews))

    def test_reviews_count_sent_to_template(self):
        # Log user in.
        self.client.force_login(self.user)
        # Creates 24 reviews
        reviews = create_reviews(self.books, self.user, n=24)
        response = self.client.get(self.my_reviews_url)
        self.assertEqual(response.context['paginator'].count, len(reviews))
