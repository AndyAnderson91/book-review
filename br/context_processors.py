from .forms import SearchForm


def search_form(request):
    q = request.GET.get('q')
    return {'search_form': SearchForm(initial={'q': q})}
