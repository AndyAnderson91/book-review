import pytest

from django.db.utils import IntegrityError
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from book_review.models import Book, Review


# Local fixtures.

@pytest.fixture
def review():
    return mixer.blend(Review)


pytestmark = pytest.mark.django_db


# Tests.

def test_rating_field_has_choices(review):
    rating = review._meta.get_field('rating').choices
    assert bool(rating) is True


def test_rating_field_choices_are_from_1_to_5(review):
    rating = review._meta.get_field('rating').choices
    assert rating == [(i, i) for i in range(1, 6)]


def test_review_unique_together_constraint():
    book, user = mixer.blend(Book), mixer.blend(User)
    mixer.blend(Review, book=book, owner=user)
    with pytest.raises(IntegrityError):
        mixer.blend(Review, book=book, owner=user)


def test_str_representation(review):
    assert str(review) == review.title
