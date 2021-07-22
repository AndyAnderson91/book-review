from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    # Born year is needed for namesake cases
    born = models.DateField()

    class Meta:
        unique_together = ['first_name', 'patronymic', 'last_name', 'born']

    def save(self, *args, **kwargs):
        if self.patronymic:
            name_parts = [self.first_name, self.patronymic, self.last_name]
        else:
            name_parts = [self.first_name, self.last_name]
        self.full_name = ' '.join(name_parts)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.last_name


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=50)
    # Book might have multiple authors, so many-to-many relationship is better
    authors = models.ManyToManyField(Author)
    genres = models.ManyToManyField(Genre)
    language = models.CharField(max_length=50)
    pub_date = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=1024, blank=True)
    # set of users who already reviewed this book, so they can't do it again.
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=40, null=True)

    class Meta:
        unique_together = ['title', 'pub_date']

    def get_absolute_url(self):
        return reverse('br:book', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify((self.title + ' ' + str(self.pub_date.year)), allow_unicode=True)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


rates = [(i, i) for i in range(1, 6)]


class Review(models.Model):
    title = models.CharField(max_length=60)
    # One review can only refer to one book while one book can have many reviews
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField(max_length=8192)
    rating = models.IntegerField(choices=rates)
    # By default, the review is available for viewing to all users
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateField(auto_now=True)
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.title
