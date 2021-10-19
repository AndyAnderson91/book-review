import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from .custom.constants import RATINGS


def get_sentinel_user():
    """
    If user is deleted replaces 'owner' field in Review model with 'deleted user' object.
    """
    return get_user_model().objects.get_or_create(username='deleted user')[0]


class Author(models.Model):
    """
    Book author model.
    """
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    born = models.DateField(
        help_text='YYYY-MM-DD',
        validators=[MaxValueValidator(limit_value=datetime.date.today)]
    )

    class Meta:
        unique_together = ['first_name', 'patronymic', 'last_name', 'born']
        ordering = ['first_name']

    def __str__(self):
        """
        String representation is an author's full name.
        """
        parts = [self.first_name, self.last_name]
        if self.patronymic:
            parts.insert(1, self.patronymic)

        return " ".join(parts)


class Genre(models.Model):
    """
    Book genre model.
    """
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model.
    """
    title = models.CharField(max_length=100)
    original_title = models.CharField(max_length=100, blank=True)
    # Book might have multiple authors, so many-to-many relationship is used.
    authors = models.ManyToManyField(Author)
    genres = models.ManyToManyField(Genre)
    language = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    # Not limiting pub_date max value by today in case of anticipated books.
    pub_date = models.DateField(help_text='YYYY-MM-DD')
    description = models.TextField(max_length=1024, blank=True)
    full_img = models.ImageField(upload_to='img/book_img/full/', default='img/book_img/full/default-book-full.jpg')
    small_img = models.ImageField(upload_to='img/book_img/small/', default='img/book_img/small/default-book-small.jpg')
    pages = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(max_length=80)

    class Meta:
        unique_together = ['title', 'pub_date']
        ordering = ['title']

    def is_published(self):
        """
        Returns True if book is already published.
        """
        return self.pub_date <= datetime.date.today()

    def get_absolute_url(self):
        # Using slug only is not safe enough since different books may have identical titles.
        # Using id only is not giving informative url for user,
        # So slug and id are used together.
        return reverse('book_review:book', kwargs={
            'pk': self.pk,
            'slug': self.slug
        })

    def __str__(self):
        return self.title


class Review(models.Model):
    """
    Review model.
    """
    title = models.CharField(max_length=60)
    # One review can only refer to one book.
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField(max_length=8192)
    rating = models.IntegerField(choices=RATINGS)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user)
    )
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        # Put unique constraint on book and owner fields,
        # since each user may only have 1 review on each book.
        unique_together = ['book', 'owner']

    def __str__(self):
        return self.title
