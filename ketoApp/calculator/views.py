"""
This file contains Django views for managing the creation, update, display, and deletion of Product and FullDayIntake
instances, as well as generating and sending email reports in PDF format. These views allow users to interact with the
application's data through forms and templates, ensuring that product macronutrient values are calculated, updated, and
displayed correctly. Additionally, users can generate PDF reports of their diet data and send them via email.

The views use Django's class-based views (CBVs), background tasks (via Celery) to process and display relevant data to
the user. The views use templates for rendering the UI and redirection for handling user navigation between pages."""
import json
from datetime import date
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, FormView, TemplateView

from .forms import EmailRequestForm, ProductRequestForm
from .models import FullDayIntake, Product
from .utils import GetConnection
from .tasks import send_report
from API.serializers import FullDayIntakeSerializer


class ProductMacroNutrientsCreate(LoginRequiredMixin, View):
    """
        View to handle creation of a Product object based on macronutrient data.

        This view allows logged-in users to enter a product name and its weight (in grams),
        retrieve macronutrient information for that product, and save the data to the database.
        """

    def post(self, request, *args, **kwargs):
        """
        POST request creates a Product instance with macronutrient information.

        This method retrieves user input from `ProductRequestForm`, validates it,
        and uses the input to get macronutrient data for the specified product.
        If the form is valid, a new `Product` object is created and saved to the database
        with the retrieved data. Redirects to the profile page upon successful form submission.
        """
        selected_date = kwargs.get('selected_date', str(date.today()))
        form = ProductRequestForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data.get('product_name')
            grams = form.cleaned_data.get('grams')
            product_request = GetConnection(product, grams).get_connection()
            product_macronutrients = Product.objects.create(
                name=product,
                grams=grams,
                kcal=product_request['calories'],
                carb=product_request['totalNutrients']['CHOCDF']['quantity'],
                fat=product_request['totalNutrients']['FAT']['quantity'],
                protein=product_request['totalNutrients']['PROCNT']['quantity'],
                date=selected_date,
            )
            product_macronutrients.user.add(self.request.user.ketoappuser)
            product_macronutrients.save()

            if selected_date == str(date.today()):
                return redirect("profile")
            else:
                return redirect(reverse("products_list_by_date", args=[selected_date]))

        return render(request, "calculator/product_nutrients_form.html", {'form': form})

    def get(self, request, *args, **kwargs):
        """
        GET request to render the product nutrient form.

        This method renders an empty `ProductRequestForm` for the user to input
        product name and grams, allowing them to submit the form with POST.
        Renders the "product_nutrients_form.html" template with an empty form.
        """
        selected_date = kwargs.get('selected_date', str(date.today()))
        form = ProductRequestForm()
        return render(request, "calculator/product_nutrients_form.html", {'form': form, 'selected_date': selected_date})


class ProductMacroNutrientsUpdate(LoginRequiredMixin, View):
    """
    View updating an existing Product object's macronutrient data.

    This view allows logged-in users to update the weight (grams) of an existing Product.
    The updated macronutrient values are retrieved based on the new weight and saved to the database.
    """

    def post(self, request, *args, **kwargs):
        """
        POST request to update an existing Product instance with new macronutrient information.

        This method validates the submitted `ProductRequestForm`, retrieves the Product object
        by its primary key (`pk`), and updates its macronutrient data based on the new weight.
        If the product date is today, the user is redirected to the profile page,
        otherwise they are redirected to a list of products by date.
        Redirects to the profile page or products list based on the product date.
        """

        form = ProductRequestForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(id=self.kwargs.get('pk'))
            grams = form.cleaned_data.get('grams')
            product_request = GetConnection(product.name, grams).get_connection()

            Product.objects.filter(id=self.kwargs.get('pk')).update(
                grams=grams,
                kcal=product_request['calories'],
                carb=product_request['totalNutrients']['CHOCDF']['quantity'],
                fat=product_request['totalNutrients']['FAT']['quantity'],
                protein=product_request['totalNutrients']['PROCNT']['quantity'],
            )

            if product.date == date.today():
                return redirect("profile")

            return redirect("products_list_by_date", product.date)

        return render(request, "calculator/product_nutrients_form.html", {'form': form})

    def get(self, request, *args, **kwargs):
        """
        GET request to render the product update form with pre-filled data.

        This method retrieves the Product instance by its primary key (`pk`), pre-fills
        the `ProductRequestForm` with the product's name, and hides the product name field in the form.
        Renders the "product_nutrients_form.html" template with a pre-filled form.
        """

        product = Product.objects.get(id=self.kwargs.get('pk'))
        form = ProductRequestForm(initial={'product_name': product.name})
        form.fields['product_name'].widget = forms.HiddenInput()
        return render(request, "calculator/product_nutrients_form.html", {'form': form})


class ProductDetailView(LoginRequiredMixin, DetailView):
    """
        This view retrieves and displays the details of a single Product object,
        including its macronutrient data, using the 'single_product_nutrients.html' template.

        Attributes:
            model (Model): The model associated with this view, set to `Product`.
            template_name (str): The path to the template used to render the view.
    """

    model = Product
    template_name = 'calculator/single_product_nutrients.html'


class ProductListByDateView(LoginRequiredMixin, TemplateView):
    """
    This view allows logged-in users to view all products associated with a specific date,
    Contains 2 buttons for handling user navigation between pages: 1. SUMMARY - full day intake data button,
    2. ADD PRODUCT - creates new product. The products are displayed using the 'list_products.html' template.

    Attributes:
        template_name (str): The path to the template used to render the list of products by date.
    """
    model = Product
    template_name = "calculator/list_products.html"

    def get_context_data(self, **kwargs):
        """
        This method retrieves the date from URL parameters, queries the Product model for all data
        associated with that date, and, if present, includes `FullDayIntake` data for that date in the context.

        Returns:
            dict: The context data for rendering the template, including:
            - 'date' (str): The date for which product data is being retrieved.
            - 'fulldayintake' (FullDayIntake or None): Full day intake data for the date, if exists.
            - 'product_by_date' (QuerySet): A queryset of Product instances for the specified date.
        """

        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs.get('date')
        if FullDayIntake.objects.filter(date=context['date']).exists():
            context['fulldayintake'] = FullDayIntake.objects.get(date=context['date'])
        context['product_by_date'] = Product.objects.filter(date=context['date'])
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """
    This view allows logged-in users to delete a `Product` entry and redirects them
    based on the date of the product being deleted. If the product's date matches the current date,
    the user is redirected to their profile page. Otherwise, they are redirected to the product list
    for the product's date.

    Attributes:
        model: The model associated with this view set to `Product`.
        template_name (str): The path to the template used to render the delete confirmation page.
    """

    model = Product
    template_name = 'calculator/delete_product_confirm.html'

    def get_success_url(self):
        """
        Determine the URL to redirect upon successful deletion of the Product instance.

        If the deleted product's date is today, the user is redirected to the profile page.
        Otherwise, the user is redirected to the list of products for the specified date.
        """

        if self.object.date == date.today():
            return reverse_lazy("profile")
        return reverse_lazy('products_list_by_date', args=[self.object.date])


class SummaryView(LoginRequiredMixin, DetailView):
    """
    This view allows logged-in users to view detailed information about their full day intake,
    including macronutrient totals. The information is rendered using the 'summary.html' template.

    Attributes:
        model: The model associated with this view, set to `FullDayIntake`.
        template_name (str): The path to the template used to render the daily intake summary.
       """

    model = FullDayIntake
    template_name = 'calculator/summary.html'

    def get_queryset(self):
        """
        This method returns the queryset of FullDayIntake instances for the logged-in user.
        """

        return FullDayIntake.objects.filter(user=self.request.user.ketoappuser)


class CalendarView(LoginRequiredMixin, TemplateView):
    """
    This view allows logged-in users to see a calendar that highlights days with
    `FullDayIntake` events. Each day with a `FullDayIntake` entry is displayed as an event
    on the calendar. The view is rendered using the 'calendar2.html' template.

    Attributes:
        template_name (str): The path to the template used to render the calendar view.
    """

    template_name = "calculator/calendar.html"

    def get_context_data(self, **kwargs):
        """
        This method retrieves all instances of `FullDayIntake` and adds them to the context
        under the 'events' key, allowing the template to render each intake entry as an event
        in the calendar.

        Returns:
            dict: The context data for rendering the template, including:
            - 'events': A queryset of all `FullDayIntake` instances.
        """

        context = super().get_context_data(**kwargs)
        serializer = FullDayIntakeSerializer(FullDayIntake.objects.filter(user=self.request.user.ketoappuser), many=True)
        context['events'] = serializer.data
        return context


class SendReportPdfView(FormView):
    """
    This view renders a form where the user provides a start and end date, as well as
    an email address. Upon form submission, a background task is triggered to generate
    the PDF report and send it to the specified email.

    Attributes:
        template_name (str): The path to the template used to render the email request form.
        form_class (Form): The form class used to collect the user's email and date range.
    """

    template_name = 'calculator/send_email.html'
    form_class = EmailRequestForm

    def form_valid(self, form):
        """
        This method is called when the form is successfully validated. It retrieves the
        `start_date`, `end_date`, and `email` from the cleaned form data and triggers
        a background task to generate the report and send it by email.

        Parameters:
            form (EmailRequestForm): The validated form containing the user's input.

        Returns:
            HttpResponse: Renders a success page that the email has been sent.
        """

        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        email = form.cleaned_data.get('email')
        user_id = self.request.user.id

        if not self.if_product_exists(start_date, end_date):
            return render(self.request, "calculator/no_product_found.html")

        send_report.delay(user_id, email, start_date, end_date)
        return render(self.request, "calculator/send_email_success.html")

    def if_product_exists(self, start, end) -> bool:
        """
        Checks if any Product instances exist within a specified date range for the logged-in user.
        """

        return Product.objects.filter(date__range=[start, end], user=self.request.user.ketoappuser).exists()
