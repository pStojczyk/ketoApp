"""
This file contains views that handle user registration, profile display and updates,
as well as managing user specific data related to daily nutritional requirements
and personal information such as weight, height, age, gender, and activity level.
"""

from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from rest_framework.authtoken.models import Token

from calculator.models import Product, FullDayIntake
from .models import Demand, KetoAppUser


class Register(CreateView):
    """
    A view that handles the user registration process.
    Inherits from `CreateView` to handle the creation of a new user.
    """

    def post(self, request, *args, **kwargs):
        """
        Processes the registration form submitted by the user. If the form is valid, a new user
        is created, and the user is redirected to the login page with a success message.
        If the form is not valid, the registration page is re-rendered.
        """

        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"You have been successfully signed up {username} !")
            return redirect('login')

        return render(request, 'users/register.html', {'form': form})

    def get(self, request, *args, **kwargs):
        """
        Renders the registration page with an empty user creation form.
        """

        form = UserCreationForm()
        return render(request, "users/register.html", {"form": form})


class Profile(LoginRequiredMixin, TemplateView):
    """
    This view is only accessible to authenticated users. It renders a template that shows
    the user's profile
    """

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        """
        Adds the necessary context data to render the user's profile page, including:
            - Current date or a date provided in the URL (selected_date).
            - The products consumed on the current date.
            - The full day intake summary (if available) for the current date.

        Returns:
            dict: The context dictionary that will be passed to the template for rendering.
        """

        context = super().get_context_data(**kwargs)
        selected_date = self.kwargs.get('selected_date', None)

        if selected_date:
            context['today'] = datetime.strptime(selected_date, '%Y-%m-%d').date()
        context['today'] = date.today()

        fulldayintake = FullDayIntake.objects.filter(date=context['today'], user=self.request.user.ketoappuser).first()

        if fulldayintake:
            context['fulldayintake'] = fulldayintake
        context['products_list'] = Product.objects.filter(date=context['today'], user=self.request.user.ketoappuser)

        token, _ = Token.objects.get_or_create(user=self.request.user)
        context['token'] = token.key

        return context


class KetoAppUserUpdateView(LoginRequiredMixin, UpdateView):
    """
    This view allows users to update their personal information such as weight,
    height, age, gender, and activity level. The user must be logged in to access this view.
    """

    model = KetoAppUser
    fields = ['weight', 'height', 'age', 'gender', 'activity']
    template_name = 'users/keto_app_user_form.html'

    def get_success_url(self):
        """Returns the URL to redirect to after the form has been successfully submitted."""
        return reverse_lazy('profile')

    def form_valid(self, form):
        """Validation for fields before saving"""

        weight = form.cleaned_data.get('weight')
        if weight is None:
            form.add_error('weight', 'This field is required.')
            return self.form_invalid(form)

        height = form.cleaned_data.get('height')
        if height is None:
            form.add_error('height', 'This field is required.')
            return self.form_invalid(form)

        age = form.cleaned_data.get('age')
        if age is None:
            form.add_error('age', 'This field is required.')
            return self.form_invalid(form)

        gender = form.cleaned_data.get('gender')
        if gender not in ['Male', 'Female']:
            form.add_error('gender', 'Invalid gender value. Please select either Male or Female.')
            return self.form_invalid(form)

        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        """Override to ensure the form with errors is passed to the template"""
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context)


class DemandDetailView(LoginRequiredMixin, DetailView):
    """
    This view shows the user's daily calories, fat, protein, and carbohydrate needs based on
    their activity level and personal information. It filters the data to only show the user's
    specific information.
    """

    model = Demand
    template_name = 'users/daily-requirements.html'

    def get_queryset(self):
        """
        This method overrides the default `get_queryset` method to ensure that the queryset
        only includes `Demand` objects that belong to the current logged-in user
        associated with the `KetoAppUser` model.
        """

        return super().get_queryset().filter(keto_app_user=self.request.user.ketoappuser)

    def get_object(self, queryset=None):
        """
        Overriding get_object to ensure that the Demand object belongs to the currently logged-in user.
        """

        obj = super().get_object(queryset)
        if obj.keto_app_user != self.request.user.ketoappuser:
            raise Http404("You do not have permission to view this demand.")
        return obj

    def get_context_data(self, **kwargs):
        """
        Ensure that the demand object is added to the context, accessible in the template.
        """

        context = super().get_context_data(**kwargs)
        context['demand'] = self.get_object()
        return context

