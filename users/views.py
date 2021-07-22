from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


class RegisterFormView(generic.edit.FormView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        new_user = form.save()
        login(self.request, new_user)
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET['next']

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('br:index')
        return super().get(request, *args, **kwargs)



