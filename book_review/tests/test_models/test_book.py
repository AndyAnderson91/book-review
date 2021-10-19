import pytest
import datetime

from django.urls import reverse
from mixer.backend.django import mixer
from django.db.utils import IntegrityError
from book_review.models import Book


# Constants.

BOOK_DATA = {
    'title': 'book',
    'pub_date': datetime.date.today() - datetime.timedelta(days=30)
}


# Local fixtures.

@pytest.fixture
def published_book():
    return mixer.blend(Book, **BOOK_DATA)


pytestmark = pytest.mark.django_db


# Tests.

def test_book_with_past_publication_date_is_published(published_book):
    assert published_book.is_published()


def test_book_with_today_publication_date_is_published():
    today = datetime.date.today()
    today_book = mixer.blend(Book, pub_date=today)
    assert today_book.is_published()


def test_book_with_future_publication_date_is_not_published():
    future_date = datetime.date.today() + datetime.timedelta(days=30)
    future_book = mixer.blend(Book, pub_date=future_date)
    assert not future_book.is_published()


def test_original_title_field_blank_is_true(published_book):
    blank = published_book._meta.get_field('original_title').blank
    assert bool(blank) is True


def test_description_field_blank_is_true(published_book):
    blank = published_book._meta.get_field('description').blank
    assert bool(blank) is True


def test_pub_date_field_help_text(published_book):
    help_text = published_book._meta.get_field('pub_date').help_text
    assert help_text == 'YYYY-MM-DD'


@pytest.mark.parametrize('image_field', ['full_img', 'small_img'])
def test_image_fields_have_default_values(published_book, image_field):
    default = published_book._meta.get_field(image_field).default
    assert bool(default) is True


def test_pages_field_blank_is_true(published_book):
    blank = published_book._meta.get_field('pages').blank
    assert bool(blank) is True


def test_pages_field_null_is_true(published_book):
    null = published_book._meta.get_field('pages').null
    assert bool(null) is True


def test_book_unique_together_constraint(published_book):
    with pytest.raises(IntegrityError):
        mixer.blend(Book, **BOOK_DATA)


def test_get_absolute_url(published_book):
    expected_url = reverse('book_review:book', kwargs={
        'pk': published_book.pk,
        'slug': published_book.slug
    })
    assert published_book.get_absolute_url() == expected_url


def test_str_representation(published_book):
    assert str(published_book) == BOOK_DATA.get('title')
