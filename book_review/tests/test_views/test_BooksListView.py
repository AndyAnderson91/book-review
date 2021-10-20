import pytest
from django.urls import reverse
from book_review.custom.constants import BOOKS_PER_PAGE


URL_ARGUMENTS = ['recent', 'popular', 'best_rated']
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('url_argument', URL_ARGUMENTS)
def test_view_is_accessible_by_name(client, url_argument):
    url = '{0}?order={1}'.format(reverse('book_review:books_list'), url_argument)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('url_argument', URL_ARGUMENTS)
def test_empty_published_books_queryset_appropriate_message(client, url_argument):
    message = 'There are no published books in app database.'
    url = '{0}?order={1}'.format(reverse('book_review:books_list'), url_argument)
    response = client.get(url)
    content = response.content.decode()
    assert message in content


@pytest.mark.parametrize('url_argument', URL_ARGUMENTS)
def test_pagination_is_on(client, url_argument, published_books):
    url = '{0}?order={1}'.format(reverse('book_review:books_list'), url_argument)
    response = client.get(url)
    assert response.context.get('is_paginated')


@pytest.mark.parametrize('url_argument', URL_ARGUMENTS)
def test_page_contains_expected_number_of_books(client, url_argument, published_books):
    url = '{0}?order={1}'.format(reverse('book_review:books_list'), url_argument)
    response = client.get(url)
    assert len(response.context.get('page_obj')) == BOOKS_PER_PAGE


@pytest.mark.parametrize('url_argument', URL_ARGUMENTS)
def test_anticipated_books_are_not_sent_to_template(client, url_argument, anticipated_books, published_books):
    url = '{0}?order={1}'.format(reverse('book_review:books_list'), url_argument)
    response = client.get(url)
    assert response.context.get('paginator').count == len(published_books)
