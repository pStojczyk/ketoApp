from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateField


def name_validator(value):
    for char in value:
        if char.isdigit():
            raise ValidationError(f"Product name can not contain digits", params={'value': value})


class ProductRequestForm(forms.Form):
    product_name = forms.CharField(label="Product", validators=[name_validator])
    grams = forms.IntegerField(label="Grams")


class EmailRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "Your e-mail"}))


class Date(forms.DateInput):
    input_type = 'date'


class CalendarForm(forms.Form):
    date = DateField(widget=Date)
