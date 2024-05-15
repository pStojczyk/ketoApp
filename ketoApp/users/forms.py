from django import forms
# from django.contrib.auth.forms import User
from .models import KetoAppUser
# from .views import UserCreationForm

# dodac do paska navbar do zmiany hasla i nazwy uzytownika, po zalogowaniu?

# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = KetoAppUser
#         fields = ['username', 'password1', 'password2']


class KetoAppUserForm(forms.ModelForm):

    class Meta:
        model = KetoAppUser
        fields = ['weight', 'height', 'age', 'gender', 'activity']

        widgets = {
            'weight': forms.NumberInput(attrs={"required": True, "class": "form-control", "placeholder": "Enter your weight in kilograms"}),
            'height': forms.NumberInput(attrs={"required": True, "class": "form-control", "placeholder": "Enter your height in centimeters"}),
            'age': forms.NumberInput(attrs={"required": True, "class": "form-control", "placeholder": "Enter your age"}),
            'gender': forms.Select(attrs={"required": True, "class": "select", "placeholder": "Select your gender"}),
            'activity': forms.Select(attrs={"required": True, "class": "select", "placeholder": "Select your activity level"}),
        }
