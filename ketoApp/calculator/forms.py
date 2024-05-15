from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateField
from django.forms import DateInput
from .models import Product


def name_validator(value):
    for char in value:
        if char.isdigit():
            raise ValidationError(f"Product name can not contain digits", params={'value': value})


class ProductRequestForm(forms.Form):
    product_name = forms.CharField(label="Enter product", validators=[name_validator])
    grams = forms.IntegerField(label="Enter grams")


class Date(forms.DateInput):
    input_type = 'date'


class CalendarForm(forms.Form):
    date = DateField(widget=Date)







