import pytest
from django.urls import reverse
from book_review.custom.constants import BOOKS_PER_PAGE


pytestmark = pytest.mark.django_db


def test_view_is_accessible_by_name(client):
    url = reverse('book_review:index')
    response = client.get(url)
    assert response.status_code == 200


def test_empty_anticipated_books_queryset_appropriate_message(client):
    url = reverse('book_review:index')
    response = client.get(url)
    message = 'No books are anticipated at the moment'
    content = response.content.decode()
    assert message in content


def test_pagination_is_on(client, anticipated_books):
    url = reverse('book_review:index')
    response = client.get(url)
    assert response.context.get('is_paginated')


def test_page_contains_expected_number_of_books(client, anticipated_books):
    url = reverse('book_review:index')
    response = client.get(url)
    assert len(response.context.get('page_obj')) == BOOKS_PER_PAGE


def test_published_books_are_not_sent_to_template(client, anticipated_books, published_books):
    url = reverse('book_review:index')
    response = client.get(url)
    assert response.context.get('paginator').count == len(anticipated_books)
