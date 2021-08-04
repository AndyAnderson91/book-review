import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted user')[0]


class Author(models.Model):
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
        if self.patronymic:
            parts = [self.first_name, self.patronymic, self.last_name]
        else:
            parts = [self.first_name, self.last_name]
        return " ".join(parts)


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=80)
    # Book might have multiple authors, so many-to-many relationship is better
    authors = models.ManyToManyField(Author)
    genres = models.ManyToManyField(Genre)
    language = models.CharField(max_length=50)
    pub_date = models.DateField(help_text='YYYY-MM-DD')
    description = models.TextField(max_length=1024, blank=True)
    full_img = models.ImageField(upload_to='img/book_img/full/', default='img/book_img/full/default-book-full.jpg')
    small_img = models.ImageField(upload_to='img/book_img/small/', default='img/book_img/small/default-book-small.jpg')
    slug = models.SlugField(max_length=80)

    class Meta:
        unique_together = ['title', 'pub_date']
        ordering = ['title']

    def is_published(self):
        return self.pub_date <= datetime.date.today()

    def get_absolute_url(self):
        return reverse('br:book', kwargs={
            'pk': self.id,
            'slug': self.slug
        })

    def __str__(self):
        return self.title


RATINGS = [(i, i) for i in range(1, 6)]


class Review(models.Model):
    title = models.CharField(max_length=60)
    # One review can only refer to one book while one book can have many reviews
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField(max_length=8192)
    rating = models.IntegerField(choices=RATINGS)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user)
    )
    pub_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ['book', 'owner']

    def __str__(self):
        return self.title
