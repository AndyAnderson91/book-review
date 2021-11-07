import pytest
from django.urls import reverse
from book_review.custom.constants import BOOKS_PER_PAGE


pytestmark = pytest.mark.django_db


def test_view_is_accessible_by_name(client):
    url = reverse('book_review:search')
    response = client.get(url)
    assert response.status_code == 200


def test_empty_search_query_appropriate_message(client):
    message = 'Empty request. Please, type something to search.'
    url = reverse('book_review:search')
    response = client.get(url)
    content = response.content.decode()
    assert message in content


def test_empty_search_result_queryset_appropriate_message(client):
    q = 'no matched query'
    message = 'Nothing found for «{0}» :('.format(q)
    url = reverse('book_review:search')
    response = client.get(url, {'q': q, 'category': 'any'})
    content = response.content.decode()
    assert message in content


def test_nonexistent_category_appropriate_message(client):
    message = 'No such category'
    url = reverse('book_review:search')
    response = client.get(url, {'q': 'book', 'category': 'non-existent category'})
    content = response.content.decode()
    assert message in content


def test_pagination_is_on(client, published_books, anticipated_books):
    url = reverse('book_review:search')
    response = client.get(url, {'q': 'book', 'category': 'any'})
    assert response.context.get('is_paginated')


def test_page_contains_expected_number_of_books(client, published_books, anticipated_books):
    url = reverse('book_review:search')
    response = client.get(url, {'q': 'book', 'category': 'any'})
    assert len(response.context.get('page_obj')) == BOOKS_PER_PAGE


def test_paginator_count_value_is_correct(client, published_books, anticipated_books):
    url = reverse('book_review:search')
    response = client.get(url, {'q': 'book', 'category': 'any'})
    assert response.context.get('paginator').count == len(published_books) + len(anticipated_books)
