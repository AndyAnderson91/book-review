import datetime

from django.test import TestCase, Client
from br.models import Book, Author, Genre, Review


class BookTestCase(TestCase):
    def setUp(self):
        Book.objects.create(title='past_book', pub_date=datetime.date.today() - datetime.timedelta(days=10))
        Book.objects.create(title='present_book', pub_date=datetime.date.today())
        Book.objects.create(title='future_book', pub_date=datetime.date.today() + datetime.timedelta(days=10))

    def test_book_is_published_method(self):
        past_book = Book.objects.get(title='past_book')
        present_book = Book.objects.get(title='present_book')
        future_book = Book.objects.get(title='future_book')

        self.assertEqual(past_book.is_published(), True)
        self.assertEqual(present_book.is_published(), True)
        self.assertEqual(future_book.is_published(), False)


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        Book.objects.create(id=1, title='Book title', pub_date=datetime.date.today())

    def test_login(self):
        with self.settings(LOGIN_URL='/login/'):
            login_response = self.client.get('/login/')
            my_reviews_response = self.client.get('/my_reviews/')
            write_review_response = self.client.get('/review/1-book-title/add/')
            edit_review_response = self.client.get('/review/1-book-title/edit/')
            delete_review_response = self.client.get('/review/1-book-title/delete/')

            self.assertEqual(login_response.status_code, 200)

            self.assertEqual(my_reviews_response.status_code, 302)
            self.assertRedirects(my_reviews_response, '/login/?next=/my_reviews/')

            self.assertEqual(write_review_response.status_code, 302)
            self.assertRedirects(write_review_response, '/login/?next=/review/1-book-title/add/')

            self.assertEqual(edit_review_response.status_code, 302)
            self.assertRedirects(edit_review_response, '/login/?next=/review/1-book-title/edit/')

            self.assertEqual(delete_review_response.status_code, 302)
            self.assertRedirects(delete_review_response, '/login/?next=/review/1-book-title/delete/')
