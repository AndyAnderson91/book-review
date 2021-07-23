from django import forms


class SimpleForm(forms.Form):
    field1 = forms.CharField(max_length=50)
    field2 = forms.CharField(max_length=50)