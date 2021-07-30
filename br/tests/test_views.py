import datetime

from django.test import TestCase
from django.urls import reverse
from br.models import Author, Book, Genre, Review
from br.views import BOOKS_PER_PAGE
from django.utils.text import slugify


class IndexListViewTest(TestCase):
    """
    Class for testing IndexListView.
    Only anticipated books should be displayed at index page.
    """
    @classmethod
    def setUpTestData(cls):
        # Creating 14 published books (shouldn't be transferred to template).
        number_of_published_books = 14
        for book_number in range(number_of_published_books):
            Book.objects.create(
                title='published book № {0}'.format(book_number),
                slug=slugify('published book № {0}'.format(book_number)),
                pub_date=datetime.date.today() - datetime.timedelta(days=book_number)
            )

    def test_index_view_url_accessible_by_name(self):
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
        books_to_show = []
        number_of_anticipated_books = 32
        for book_number in range(number_of_anticipated_books):
            books_to_show.append(Book.objects.create(
                title='anticipated book № {0}'.format(book_number),
                slug=slugify('published book № {0}'.format(book_number)),
                pub_date=datetime.date.today() + datetime.timedelta(days=(book_number + 1))
            ))

        response = self.client.get(reverse('br:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['anticipated_books']), BOOKS_PER_PAGE)
        self.assertEqual(response.context['paginator'].count, len(books_to_show))


class BooksListViewTest(TestCase):
    """
    Class for testing BooksListView
    This view is used by 3 urls: /recent/, /popular/, /best_rated/
    Each url defines sort type of published books.
    Only published books can be displayed.
    """

    # def test_accessible_by_recent_url(self):
    #     response = self.client.get(reverse('br:books_list', args=('recent',)))
    #     self.assertEqual(response.status_code, 200)
