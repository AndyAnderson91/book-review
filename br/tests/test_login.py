import datetime

from django.test import TestCase, Client
from django.contrib.auth.models import User
from br.models import Book


class LoginTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_login(self):
        login = self.client.force_login(User.objects.get_or_create(username='tester')[0])



class LoginTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Book.objects.create(
            id=1,
            title='Book title',
            pub_date=datetime.date.today()
        )

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
