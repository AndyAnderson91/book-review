import pytest
import datetime

from mixer.backend.django import mixer
from django.contrib.auth.models import User
from book_review.models import Book, Review


# Book fixtures.

@pytest.fixture
def anticipated_books():
    pub_date = datetime.date.today() + datetime.timedelta(days=30)
    return mixer.cycle(40).blend(Book, pub_date=pub_date, title=mixer.sequence("anticipated_book{0}"))


@pytest.fixture
def published_books():
    pub_date = datetime.date.today() - datetime.timedelta(days=30)
    return mixer.cycle(50).blend(Book, pub_date=pub_date, title=mixer.sequence("published_book{0}"))


@pytest.fixture
def anticipated_book(anticipated_books):
    return anticipated_books[0]


@pytest.fixture
def published_book(published_books):
    return published_books[0]


# User fixtures.

@pytest.fixture
def user():
    return mixer.blend(User)


# Review fixtures.

@pytest.fixture
def reviews_owned_by_user(user):
    return mixer.cycle(60).blend(Review, owner=user)


@pytest.fixture
def published_book_reviews(published_book):
    return mixer.cycle(70).blend(Review, book=published_book)


@pytest.fixture
def published_book_review_owned_by_user(user, published_book):
    return mixer.blend(Review, owner=user, book=published_book)
