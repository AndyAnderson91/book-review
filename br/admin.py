from django.contrib import admin
from .models import Author, Genre, Book, Review


class BookAuthor(admin.TabularInline):
    model = Book.author.through


class BookGenre(admin.TabularInline):
    model = Book.genre.through


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
        BookGenre
    ]
    exclude = ('author', 'genre',)


admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Genre, GenreAdmin)
