import pytest
from book_review.models import Review
from django.urls import reverse


pytestmark = pytest.mark.django_db
REVIEW_DATA = {
    'title': 'Review title',
    'text': 'Review text',
    'rating': 5,
}


def test_unauthenticated_user_get_request_is_redirected(client, published_book):
    url = reverse('book_review:add_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    response = client.get(url)
    assert response.status_code == 302


def test_unauthenticated_user_post_request_is_redirected(client, published_book):
    url = reverse('book_review:add_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    response = client.post(url, REVIEW_DATA)
    assert response.status_code == 302


def test_unauthenticated_user_is_redirected_to_proper_url(client, published_book):
    url = reverse('book_review:add_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    response = client.get(url)
    redirect_url = '{0}?next=/review{1}add/'.format(
        reverse('users:login')[:-1],
        published_book.get_absolute_url()[5:]
    )
    assert response.get('location') == redirect_url


def test_authenticated_user_without_review_get_request_ok(client, user, published_book):
    url = reverse('book_review:add_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


def test_authenticated_user_without_review_post_request_creates_new_review(client, user, published_book):
    url = reverse('book_review:add_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    initial_number_of_reviews = len(Review.objects.all())
    client.post(url, REVIEW_DATA)
    assert len(Review.objects.all()) == initial_number_of_reviews + 1


def test_created_review_contains_correct_data(client, user, published_book):
    url = reverse('book_review:add_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    client.post(url, REVIEW_DATA)
    created_review = Review.objects.filter(
        rating=REVIEW_DATA['rating'],
        title=REVIEW_DATA['title'],
        text=REVIEW_DATA['text']
    )
    assert created_review


@pytest.mark.django_db
def test_authenticated_user_cant_add_his_second_review_for_one_book(client, user, published_book, published_book_review_owned_by_user):
    url = reverse('book_review:add_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
