import pytest
import datetime
import django.db.utils

from mixer.backend.django import mixer
from django.core.exceptions import ValidationError

from book_review.models import Author


# Constants.

FULL_NAME_AUTHOR_DATA = {
        'first_name': 'John',
        'patronymic': 'Jonah',
        'last_name': 'Jameson',
        'born': datetime.date(1970, 1, 1)
}
SHORT_NAME_AUTHOR_DATA = {
        'first_name': 'Peter',
        'patronymic': '',
        'last_name': 'Parker',
        'born': datetime.date(1990, 1, 1)
}


# Local fixtures.

@pytest.fixture
def full_name_author():
    return mixer.blend(Author, **FULL_NAME_AUTHOR_DATA)


@pytest.fixture
def short_name_author():
    return mixer.blend(Author, **SHORT_NAME_AUTHOR_DATA)


pytestmark = pytest.mark.django_db


# Tests.

def test_author_unique_together_constraint_with_full_name(full_name_author):
    with pytest.raises(django.db.utils.IntegrityError):
        mixer.blend(Author, **FULL_NAME_AUTHOR_DATA)


def test_author_unique_together_constraint_with_short_name(short_name_author):
    with pytest.raises(django.db.utils.IntegrityError):
        mixer.blend(Author, **SHORT_NAME_AUTHOR_DATA)


def test_author_str_representation_with_full_name(full_name_author):
    expected_full_name = "{0} {1} {2}".format(
        full_name_author.first_name,
        full_name_author.patronymic,
        full_name_author.last_name
    )
    assert str(full_name_author) == expected_full_name


def test_author_str_representation_with_short_name(short_name_author):
    expected_short_name = "{0} {1}".format(
        short_name_author.first_name,
        short_name_author.last_name
    )
    assert str(short_name_author) == expected_short_name


def test_patronymic_field_blank_is_true(full_name_author):
    blank = full_name_author._meta.get_field('patronymic').blank
    assert blank is True


def test_born_field_help_text(full_name_author):
    help_text = full_name_author._meta.get_field('born').help_text
    assert help_text == 'YYYY-MM-DD'


@pytest.mark.parametrize('days', [1, 10, 100, 1000])
def test_born_field_max_value_validator(days):
    future_date = datetime.date.today() + datetime.timedelta(days=days)
    author = Author.objects.create(born=future_date)
    with pytest.raises(ValidationError):
        author.full_clean()
