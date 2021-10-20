import pytest
from django.urls import reverse
from book_review.custom.constants import REVIEWS_PER_PAGE


pytestmark = pytest.mark.django_db


def test_unauthenticated_user_get_request_is_redirected(client):
    url = reverse('book_review:my_reviews')
    response = client.get(url)
    assert response.status_code == 302


def test_unauthenticated_user_is_redirected_to_proper_url(client):
    url = reverse('book_review:my_reviews')
    response = client.get(url)
    redirect_url = '{0}?next=/my_reviews/'.format(reverse('users:login')[:-1])
    assert response.get('location') == redirect_url


def test_authenticated_user_get_request_ok(client, user):
    url = reverse('book_review:my_reviews')
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


def test_empty_review_queryset_appropriate_message(client, user):
    url = reverse('book_review:my_reviews')
    client.force_login(user)
    response = client.get(url)
    message = "I haven't written reviews yet."
    content = response.content.decode()
    assert message in content


def test_pagination_is_on(client, user, reviews_owned_by_user):
    url = reverse('book_review:my_reviews')
    client.force_login(user)
    response = client.get(url)
    assert response.context.get('is_paginated')


def test_page_contains_expected_number_of_reviews(client, user, reviews_owned_by_user):
    url = reverse('book_review:my_reviews')
    client.force_login(user)
    response = client.get(url)
    assert len(response.context.get('page_obj')) == REVIEWS_PER_PAGE


def test_all_user_reviews_are_sent_to_template(client, user, reviews_owned_by_user):
    url = reverse('book_review:my_reviews')
    client.force_login(user)
    response = client.get(url)
    assert response.context.get('paginator').count == len(reviews_owned_by_user)
