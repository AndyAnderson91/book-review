import pytest
from book_review.custom.constants import REVIEWS_PER_PAGE


pytestmark = pytest.mark.django_db


def test_view_is_accessible_by_name(client, published_book):
    url = published_book.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200


def test_book_is_sent_to_template(client, published_book):
    url = published_book.get_absolute_url()
    response = client.get(url)
    assert response.context.get('book')


def test_published_book_with_no_reviews_appropriate_message(client, published_book):
    message = 'No reviews yet'
    url = published_book.get_absolute_url()
    response = client.get(url)
    content = response.content.decode()
    assert message in content


def test_anticipated_book_appropriate_message(client, anticipated_book):
    message = 'Reviews can be written as soon as the book is published'
    url = anticipated_book.get_absolute_url()
    response = client.get(url)
    content = response.content.decode()
    assert message in content


def test_pagination_is_on(client, published_book, published_book_reviews):
    url = published_book.get_absolute_url()
    response = client.get(url)
    assert response.context.get('is_paginated')


def test_page_contains_expected_number_of_reviews(client, published_book, published_book_reviews):
    url = published_book.get_absolute_url()
    response = client.get(url)
    assert len(response.context.get('page_obj')) == REVIEWS_PER_PAGE


def test_book_reviews_are_sent_to_template(client, published_book, published_book_reviews):
    url = published_book.get_absolute_url()
    response = client.get(url)
    assert response.context.get('paginator').count == len(published_book_reviews)
