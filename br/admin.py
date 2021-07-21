from django.contrib import admin
from .models import Author, Genre, Book, Review


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 2


class BookAuthor(admin.TabularInline):
    model = Book.author.through
    extra = 1


class BookGenre(admin.TabularInline):
    model = Book.genre.through
    extra = 1


class AuthorAdmin(admin.ModelAdmin):
    inlines = [
        BookAuthor,
    ]


class GenreAdmin(admin.ModelAdmin):
    inlines = [
        BookGenre,
    ]


class BookAdmin(admin.ModelAdmin):
    inlines = [
        BookAuthor,
        BookGenre,
        ReviewInline
    ]
    exclude = ('author', 'genre',)


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review)
