from django.contrib import admin

from .models import Author, Genre, Book, Review


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 1


class BookAuthor(admin.TabularInline):
    model = Book.authors.through
    extra = 1


class BookGenre(admin.TabularInline):
    model = Book.genres.through
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
    prepopulated_fields = {
        'slug': ('title',)
    }
    inlines = [
        BookAuthor,
        BookGenre,
        ReviewInline
    ]
    exclude = ('authors', 'genres')


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review)
