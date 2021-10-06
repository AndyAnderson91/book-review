from .forms import SearchForm


def search_form(request):
    """
    Allows to display search form on every page, that extends base.html.
    """
    q = request.GET.get('q')
    return {'search_form': SearchForm(initial={'q': q})}
