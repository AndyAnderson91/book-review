import datetime

from django.test import TestCase
from django.utils.text import slugify
from django.contrib.auth.models import User
from br.models import Author, Book, Genre, Review


class AuthorTestCase(TestCase):
    """
    Class for testing Author model.
    """
    @classmethod
    def setUpTestData(cls):
        # Author with full name.
        cls.full_name_author = Author.objects.create(
            id=1,
            first_name='Anton',
            patronymic='Pavlovich',
            last_name='Chekhov',
            born=datetime.date(1860, 1, 17)
        )
        # Author with short name.
        cls.short_name_author = Author.objects.create(
            id=2,
            first_name='Jack',
            last_name='London',
            born=datetime.date(1876, 1, 12)
        )

    def test_unique_together_full_name(self):
        """
        Expects Exception raising since Author model has unique_together constraint on [first_name, patronymic, last_name, born].
        """
        with self.assertRaises(Exception):
            Author.objects.create(
                first_name='Anton',
                patronymic='Pavlovich',
                last_name='Chekhov',
                born=datetime.date(1860, 1, 17)
            )

    def test_unique_together_short_name(self):
        """
        Expects Exception raising since Author model has unique_together constraint on [first_name, patronymic, last_name, born].
        """
        with self.assertRaises(Exception):
            Author.objects.create(
                first_name='Jack',
                last_name='London',
                born=datetime.date(1876, 1, 12)
            )

    def test_str_representation_full_name(self):
        """
        Expects 'first_name patronymic last_name' str representation for authors with patronymic field filled.
        """
        expected_full_name = "{0} {1} {2}".format(
            self.full_name_author.first_name,
            self.full_name_author.patronymic,
            self.full_name_author.last_name
        )
        self.assertEqual(expected_full_name, str(self.full_name_author))

    def test_str_representation_short_name(self):
        """
        Expects 'first_name last_name' str representation for authors with patronymic field empty.
        """
        expected_short_name = "{0} {1}".format(
            self.short_name_author.first_name,
            self.short_name_author.last_name
        )
        self.assertEqual(expected_short_name, str(self.short_name_author))


class BookTestCase(TestCase):
    """
    Class for testing Book model.
    """
    @classmethod
    def setUpTestData(cls):
        # Book published some time ago.
        cls.past_book = Book.objects.create(
            title='past book',
            slug=slugify('past book'),
            pub_date=datetime.date.today() - datetime.timedelta(days=10)
        )
        # Book published today.
        cls.today_book = Book.objects.create(
            title='today book',
            slug=slugify('today book'),
            pub_date=datetime.date.today()
        )
        # Book to be released in the future.
        cls.future_book = Book.objects.create(
            title='future book',
            slug=slugify('future book'),
            pub_date=datetime.date.today() + datetime.timedelta(days=10)
        )
        cls.books = [cls.past_book, cls.today_book, cls.future_book]

    def test_past_book_is_published(self):
        self.assertTrue(self.past_book.is_published())

    def test_today_book_is_published(self):
        self.assertTrue(self.today_book.is_published())

    def test_future_book_is_not_published(self):
        self.assertFalse(self.future_book.is_published())

    def test_unique_together(self):
        """
        Expects Exception raising since Book model has unique_together constraint on [title, pub_date]
        """
        with self.assertRaises(Exception):
            Book.objects.create(
                title='today book',
                slug=slugify('today book'),
                pub_date=datetime.date.today()
            )

    def test_get_absolute_url(self):
        for book in self.books:
            response = self.client.get(book.get_absolute_url())
            self.assertEqual(response.status_code, 200)


class GenreTestCase(TestCase):
    """
    Class for testing Genre model.
    """
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='novel')

    def test_unique_name(self):
        """
        Expects Exception raising since genre name is unique.
        """
        with self.assertRaises(Exception):
            Genre.objects.create(name='novel')


class ReviewTestCase(TestCase):
    """
    Class for testing Review model.
    """
    @classmethod
    def setUpTestData(cls):
        book = Book.objects.create(
            title='book',
            pub_date=datetime.date.today(),
        )
        owner = User.objects.create_user(
            username='andy',
            password='1'
        )
        Review.objects.create(
            book=book,
            owner=owner,
            rating=5
        )

    def test_unique_together(self):
        """
        Expects Exception raising since book may have only 1 review per user
        """
        with self.assertRaises(Exception):
            Review.objects.create(
                book=Book.objects.get(title='book'),
                owner=User.objects.get(username='andy')
            )
