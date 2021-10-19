import pytest
from book_review.models import Review
from django.urls import reverse


pytestmark = pytest.mark.django_db
REVIEW_UPDATE_DATA = {
    'title': 'Review updated title',
    'text': 'Review updated text',
    'rating': 4,
}


def test_unauthenticated_user_get_request_is_redirected(client, published_book):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    response = client.get(url)
    assert response.status_code == 302


def test_unauthenticated_user_post_request_is_redirected(client, published_book):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    response = client.post(url, REVIEW_UPDATE_DATA)
    assert response.status_code == 302


def test_unauthenticated_user_is_redirected_to_proper_url(client, published_book):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    response = client.get(url)
    redirect_url = '{0}?next=/review{1}edit/'.format(
        reverse('users:login')[:-1],
        published_book.get_absolute_url()[5:]
    )
    assert response.get('location') == redirect_url


def test_authenticated_user_without_review_get_request_raises_404(client, user, published_book):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


def test_authenticated_user_without_review_post_request_raises_404(client, user, published_book):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    response = client.post(url, REVIEW_UPDATE_DATA)
    assert response.status_code == 404


def test_authenticated_user_with_review_get_request_ok(client, user, published_book_review_owned_by_user):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book_review_owned_by_user.book.id,
        'slug': published_book_review_owned_by_user.book.slug
    })
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


def test_authenticated_user_with_review_post_request_doesnt_create_new_review(client, user, published_book, published_book_review_owned_by_user):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    initial_number_of_reviews = len(Review.objects.all())
    client.post(url, REVIEW_UPDATE_DATA)
    assert len(Review.objects.all()) == initial_number_of_reviews


def test_updated_review_contains_correct_data(client, user, published_book, published_book_review_owned_by_user):
    url = reverse('book_review:edit_review', kwargs={
        'pk': published_book.id,
        'slug': published_book.slug
    })
    client.force_login(user)
    client.post(url, REVIEW_UPDATE_DATA)
    updated_review = Review.objects.filter(
        rating=REVIEW_UPDATE_DATA['rating'],
        title=REVIEW_UPDATE_DATA['title'],
        text=REVIEW_UPDATE_DATA['text']
    )
    assert updated_review
