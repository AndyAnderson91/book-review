import datetime

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from br.models import Author, Book, Genre, Review
from br.views import BOOKS_PER_PAGE
from django.utils.text import slugify


def create_books(n, published):
    """
    n - amount of books to create,
    published - boolean variable. True if published books are needed, False otherwise.
    """
    books = []
    if published:
        direction = -1
    else:
        direction = 1
    for book_number in range(n):
        books.append(Book.objects.create(
            title='book №{0}'.format(book_number),
            slug=slugify('book №{0}'.format(book_number)),
            pub_date=datetime.date.today() + direction * datetime.timedelta(days=(book_number + 1))
        ))
    return books


class IndexListViewTest(TestCase):
    """
    Class for testing IndexListView.
    Only anticipated books should be displayed at index page.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Creating 14 published books (shouldn't be transferred to template).
        """
        cls.published_books = create_books(14, published=True)

    def test_index_view_url_accessible_by_name(self):
        """
        Tests reverse using view name.
        """
        response = self.client.get(reverse('br:index'))
        self.assertEqual(response.status_code, 200)

    def test_no_anticipated_books(self):
        """
        If no anticipated books, an appropriate message is displayed.
        """
        response = self.client.get(reverse('br:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No books are anticipated at the moment')
        self.assertQuerysetEqual(response.context['anticipated_books'], [])

    def test_anticipated_books(self):
        """
        If anticipated books exist, they transferred to template.
        Pagination is on, so every page displays amount of books defined by BOOKS_PER_PAGE.
        """
        # Creating 32 anticipated books.
        anticipated_books = create_books(32, published=False)
        response = self.client.get(reverse('br:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['anticipated_books']), BOOKS_PER_PAGE)
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
        """
        Creating 27 anticipated books (shouldn't be transferred to template).
        """
        cls.anticipated_books = create_books(27, published=False)

    def test_no_published_books(self):
        """
        If no published books, an appropriate message is displayed.
        """
        for url_arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(url_arg,)))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'No published books are added to site')
            self.assertQuerysetEqual(response.context['books'], [])

    def test_published_books(self):
        """
        If published books exist, they transferred to template.
        Pagination is on, so every page displays amount of books defined by BOOKS_PER_PAGE.
        """
        # Creating 49 published books.
        published_books = create_books(49, published=True)

        for url_arg in ['recent', 'popular', 'best_rated']:
            response = self.client.get(reverse('br:books_list', args=(url_arg,)))
            self.assertEqual(response.status_code, 200)
            self.assertTrue('is_paginated' in response.context)
            self.assertTrue(response.context['is_paginated'])
            self.assertEqual(len(response.context['books']), BOOKS_PER_PAGE)
            self.assertEqual(response.context['paginator'].count, len(published_books))


class BookDetailViewTest(TestCase):
    """
    Class for testing BookDetailView.
    Every book is accessible with query_pk_and_slug = True
    """

    @classmethod
    def setUpTestData(cls):
        """
        Creating 1 published and 1 anticipated books
        """
        cls.published_book = create_books(1, published=True)[0]
        cls.published_book_url = reverse('br:book', kwargs={
            'pk': cls.published_book.id,
            'slug': cls.published_book.slug
        })

        cls.anticipated_book = create_books(1, published=False)[0]
        cls.anticipated_book_url = reverse('br:book', kwargs={
            'pk': cls.anticipated_book.id,
            'slug': cls.anticipated_book.slug
        })

    def test_book_url_accessible_by_name(self):
        """
        Only published books may have reviews.
        If book has reviews, they're displayed on book detail page.
        """
        response = self.client.get(self.published_book_url)
        self.assertEqual(response.status_code, 200)

    def test_published_book_with_no_reviews(self):
        """
        Tests book detail page with no reviews.
        """
        response = self.client.get(self.published_book_url)
        self.assertContains(response, 'No reviews yet')
        self.assertEqual(response.context['reviews'], [])

    def test_published_book_with_review(self):
        """
        Tests book detail page with reviews.
        """
        review = Review.objects.create(
            title='review title',
            text='review text',
            rating='5',
            book=self.published_book,
            owner=User.objects.create_user(username='andy', password='1')
        )
        response = self.client.get(self.published_book_url)
        self.assertEqual(response.context['reviews'], [review])

    def test_anticipated_book(self):
        """
        Anticipated book can't be reviewed.
        So there is a message on review section of book detail page:
        Reviews can be written as soon as the book is published.
        """
        response = self.client.get(self.anticipated_book_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reviews can be written as soon as the book is published')
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
        cls.new_review_data1 = {
            'rating': '5',
            'title': 'review_title1',
            'text': 'review_text1',
            'book': cls.book,
            'owner': cls.user
        }
        cls.new_review_data2 = {
            'rating': '4',
            'title': 'review_title2',
            'text': 'review_text2',
            'book': cls.book,
            'owner': cls.user
        }

    def test_non_authenticated_user(self):
        """
        Non authenticated users should be redirected to login page with 'next' parameter,
        """
        response = self.client.get(self.write_review_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '{0}?next=/review{1}add/'.format(
            reverse('users:login')[:-1],
            self.book.get_absolute_url()[5:])
                         )

    def test_authenticated_user(self):
        """
        Authenticated users can get write review page and write a review on a book,
        if they haven't reviewed it yet.
        """

    def test_authenticated_user_with_no_reviews_get(self):
        """
        Authenticated user has access to write review page unless he already reviewed this book.
        """
        # Log user in.
        self.client.force_login(self.user)
        response = self.client.get(self.write_review_url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_with_no_reviews_post(self):
        """
        Authenticated user can write review on a book unless he already did it.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Check there is no reviews.
        self.assertEqual(len(Review.objects.all()), 0)
        # Posting data to CreateView built-in form.
        response = self.client.post(self.write_review_url, self.new_review_data1)
        # After adding review, user is redirected to book page.
        self.assertEqual(response.status_code, 302)
        # Check review is created.
        self.assertEqual(len(Review.objects.all()), 1)

    def test_authenticated_user_with_review_post(self):
        """
        User cant have more than one review on every book.
        """
        # Log user in.
        self.client.force_login(self.user)
        # Creating first review.
        Review.objects.create(**self.new_review_data1)
        # If user will try to get write review page again he will be redirected.
        response = self.client.get(self.write_review_url)
        self.assertEqual(response.status_code, 302)

        # Cant post another review on same book coz unique_together constraint on ['owner', 'book'] gonna fail.
        with self.assertRaises(Exception):
            self.client.post(self.write_review_url, self.new_review_data2)




