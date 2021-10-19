import pytest
from book_review.forms import SearchForm


@pytest.mark.parametrize('query', [
    'chekhov',
    'ernest hemingway',
    'erich maria remarque',
    0,
    1984,
    '22'
])
def test_valid_query(query):
    form = SearchForm(data={'q': query})
    assert form.is_valid()


def test_blank_query_is_not_valid():
    form = SearchForm(data={'q': ''})
    assert not form.is_valid()


def test_too_long_query_is_not_valid():
    form = SearchForm(data={'q': 'a'*100})
    assert not form.is_valid()


def test_query_field_has_correct_max_length_value():
    max_length = 50
    form = SearchForm()
    assert 'maxlength="{0}"'.format(max_length) in form.as_p()


def test_query_field_has_correct_placeholder():
    form = SearchForm()
    assert 'placeholder="Book, author, genre, year..."' in form.as_p()


def test_query_field_has_correct_type():
    form = SearchForm()
    assert 'type="text"' in form.as_p()
