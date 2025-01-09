"""
This file contains form classes for handling user input in the application.
Each form class is used to collect data, validate it, and make sure it's in the correct
format for use in the application.
"""

from django import forms
from django.core.exceptions import ValidationError


def name_validator(value):
    """
    This function checks each character in the product name and raises a
    ValidationError if any digit is found.
    """
    for char in value:
        if char.isdigit():
            raise ValidationError(f"Product name can not contain digits", params={'value': value})


class ProductRequestForm(forms.Form):
    """
    This form validates that the product name does not contain any digits
    and accepts the weight of the product in grams as an integer.
    """

    product_name = forms.CharField(label="Product", validators=[name_validator])
    grams = forms.IntegerField(label="Grams")


class DateInput(forms.DateInput):
    """
    This class inherits from `forms.DateInput` and specifies the input type
    as 'date', enabling the use of a date picker in supported browsers.
    """

    input_type = 'date'


class EmailRequestForm(forms.Form):
    """
    This form includes fields to specify the start and end date for the report,
    as well as an email address to which the report will be sent.
    """

    start_date = forms.DateField(widget=DateInput)
    end_date = forms.DateField(widget=DateInput)
    email = forms.EmailField(widget=forms.TextInput)
