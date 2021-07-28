import datetime

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    # Born year is needed for namesake cases
    born = models.DateField()

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
    pub_date = models.DateField()
    description = models.TextField(max_length=1024, blank=True)
    slug = models.SlugField(max_length=80)

    class Meta:
        unique_together = ['title', 'pub_date']

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
    # By default, the review is available for viewing to all users
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ['book', 'owner']

    def __str__(self):
        return self.title
