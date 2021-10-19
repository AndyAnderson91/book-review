import pytest

from django.db.utils import IntegrityError
from mixer.backend.django import mixer
from book_review.models import Genre


# Constants

GENRE_DATA = {'name': 'novel'}


# Local fixtures.

@pytest.fixture
def genre():
    return mixer.blend(Genre, **GENRE_DATA)


pytestmark = pytest.mark.django_db


# Tests.

def test_name_field_unique_is_true(genre):
    unique = genre._meta.get_field('name').unique
    assert bool(unique) is True


def test_genre_unique_constraint(genre):
    with pytest.raises(IntegrityError):
        mixer.blend(Genre, **GENRE_DATA)


def test_str_representation(genre):
    assert str(genre) == genre.name
