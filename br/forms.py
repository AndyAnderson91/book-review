from django import forms


class SearchForm(forms.Form):
    """
    Sends data to SearchListView via GET method.
    """
    q = forms.CharField(max_length=50, label='', widget=forms.TextInput(attrs={
        'placeholder': 'Book, author, genre, year...',
        'class': 'form-control search-form',
    }),
                        )
