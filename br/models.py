import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    # Born year is needed for namesake cases
    born = models.IntegerField(validators=[MinValueValidator(0), max_value_current_year], null=True, blank=True)

    class Meta:
        unique_together = ['first_name', 'patronymic', 'last_name', 'born']

    def __str__(self):
        return self.last_name


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=50)
    # Book might have multiple authors, so many-to-many relationship is better
    author = models.ManyToManyField(Author)
    genre = models.ManyToManyField(Genre)
    language = models.CharField(max_length=50)
    year = models.IntegerField(validators=[MinValueValidator(0), max_value_current_year])
    # set of users who already reviewed this book, so they can't do it again.
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['title', 'year']

    def __str__(self):
        return self.title


score_choices = [(i, i) for i in range(1, 6)]


class Review(models.Model):
    title = models.CharField(max_length=60)
    # One review can only refer to one book while one book can have many reviews
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField(max_length=8192)
    rating = models.IntegerField(choices=score_choices)
    # By default, the review is available for viewing to all users
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.title
