import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


def get_sentinel_user():
    """
    If user is deleted replaces 'owner' field in Review model with 'deleted user' object.
    """
    return get_user_model().objects.get_or_create(username='deleted user')[0]


class Author(models.Model):
    """
    Book author model.
    Born field is not shown anywhere on site,
    but is needed for unique_together constraint.
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

    def __str__(self):
        """
        String representation is an author's full name.
        """
        if self.patronymic:
            parts = [self.first_name, self.patronymic, self.last_name]
        else:
            parts = [self.first_name, self.last_name]
        return " ".join(parts)


class Genre(models.Model):
    """
    Book genre model.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model.
    """
    title = models.CharField(max_length=80)
    original_title = models.CharField(max_length=80)
    # Book might have multiple authors, so many-to-many relationship is chosen.
    authors = models.ManyToManyField(Author)
    genres = models.ManyToManyField(Genre)
    language = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    # Not limiting pub_date max value by today in case of anticipated books.
    pub_date = models.DateField(help_text='YYYY-MM-DD')
    publisher = models.CharField(max_length=80, null=True, blank=True)
    description = models.TextField(max_length=1024, blank=True)
    # Using unnamed book images by default.
    full_img = models.ImageField(upload_to='img/book_img/full/', default='img/book_img/full/default-book-full.jpg')
    small_img = models.ImageField(upload_to='img/book_img/small/', default='img/book_img/small/default-book-small.jpg')
    pages = models.PositiveIntegerField(null=True, blank=True)
    # Using slug for better url.
    slug = models.SlugField(max_length=80)

    class Meta:
        # Title and pub_date should be enough for unique constraint.
        unique_together = ['title', 'pub_date']
        # Default ordering.
        ordering = ['title']

    def is_published(self):
        """
        Returns True if book is already published. False if anticipated
        """
        return self.pub_date <= datetime.date.today()

    def get_absolute_url(self):
        """
        Slug only is not enough coz 2 books with same titles are possible,
        so id is added.
        """
        return reverse('br:book', kwargs={
            'pk': self.id,
            'slug': self.slug
        })

    def __str__(self):
        return self.title


# 5 point rating system.
RATINGS = [(i, i) for i in range(1, 6)]


class Review(models.Model):
    """
    Review model. Unique constraint is on book-owner pair,
    since each user can only have 1 review on each book once.
    Review may be edited or deleted.
    """
    title = models.CharField(max_length=60)
    # One review can only refer to one book while one book can have many reviews
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField(max_length=8192)
    rating = models.IntegerField(choices=RATINGS)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user)
    )
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['book', 'owner']

    def __str__(self):
        return self.title
