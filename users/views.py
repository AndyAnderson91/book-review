from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


class RegisterFormView(generic.edit.FormView):
    """
    Create new user and log him in.
    """
    form_class = UserCreationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        new_user = form.save()
        login(self.request, new_user)
        return super().form_valid(form)

    def get_success_url(self):
        index_url = reverse('book_review:index')
        return self.request.GET.get('next', index_url)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('book_review:index')
        return super().get(request, *args, **kwargs)



