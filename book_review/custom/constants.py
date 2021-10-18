"""
This module contains constants values used in application.
"""

# Rating values are used in Review model.
RATINGS = [(i, i) for i in range(1, 6)]

# Pagination constants are used by view classes.
BOOKS_PER_PAGE = 5
REVIEWS_PER_PAGE = 5

# Search constants are used by SearchListView class.
SEARCH_CATEGORIES = ['book', 'author', 'genre', 'year', 'any']
