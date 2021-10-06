from django.test import TestCase
from book_review.forms import SearchForm


class SearchFormTestCase(TestCase):
    """
    Class for testing SearchForm.
    """

    def test_valid_data_str(self):
        """
        Tests form if valid data is provided.
        """
        form = SearchForm(data={
            'q': 'chekhov',
            'category': 'any'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_data_blank(self):
        """
        Tests form if invalid data is provided.
        """
        form = SearchForm(data={
            'q': '',
            'category': 'any'
        })
        self.assertFalse(form.is_valid())

    def test_invalid_data_none(self):
        """
        Tests form if invalid data is provided.
        """
        form = SearchForm(data={
            'q': None,
            'category': 'any'
        })
        self.assertFalse(form.is_valid())

    def test_too_long_request_string(self):
        """
        Max_length=50.
        """
        form = SearchForm(data={
            'q': 'a'*100,
            'category': 'any'
        })
        self.assertFalse(form.is_valid())
