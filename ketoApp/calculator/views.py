import datetime
import io
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, FormView, TemplateView

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .forms import EmailRequestForm, ProductRequestForm
from .models import FullDayIntake, Product
from .utils import GetConnection
from ketoApp.settings import DEFAULT_FROM_EMAIL


class ProductMacroNutrientsCreate(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
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
            )
            product_macronutrients.save()

            return redirect("profile")

        return render(request, "calculator/product_nutrients_form.html", {'form': form})

    def get(self, request, *args, **kwargs):
        form = ProductRequestForm(request.POST)
        return render(request, "calculator/product_nutrients_form.html", {'form': form})


class ProductMacroNutrientsUpdate(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
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
            if product.date == datetime.date.today():
                return redirect("profile")
            return redirect("products_list_by_date", product.date)

        return render(request, "calculator/product_nutrients_form.html", {'form': form})

    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=self.kwargs.get('pk'))
        form = ProductRequestForm(initial={'product_name': product.name})
        form.fields['product_name'].widget = forms.HiddenInput()
        return render(request, "calculator/product_nutrients_form.html", {'form': form})


class ProductDetailView(DetailView):
    model = Product
    template_name = 'calculator/single_product_nutrients.html'


class ProductListByDateView(LoginRequiredMixin, TemplateView):
    template_name = "calculator/list_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs.get('date')
        if FullDayIntake.objects.filter(date=context['date']).exists():
            context['fulldayintake'] = FullDayIntake.objects.get(date=context['date'])
        context['product_by_date'] = Product.objects.filter(date=context['date'])
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'calculator/delete_product_confirm.html'

    def get_success_url(self):
        if self.object.date == datetime.date.today():
            return reverse_lazy("profile")
        return reverse_lazy('products_list_by_date', args=[self.object.date])


class SummaryView(LoginRequiredMixin, DetailView):
    model = FullDayIntake
    template_name = 'calculator/summary.html'


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = "calculator/calendar2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = FullDayIntake.objects.all()
        return context


class AllEventsView(View):
    def get(self, request):
        events = FullDayIntake.objects.all()
        out = []
        for event in events:
            out.append({
                'title': f'\n\nTOTAL KCAL: {event.total_kcal}\nTOTAL FAT: {event.total_fat}\nTOTAL PROTEIN: {event.total_protein}\n'
                         f'TOTAL CARBS: {event.total_carbs}',
                'start': event.date,
                'url': reverse_lazy('products_list_by_date', args=[event.date]),

            })

        return JsonResponse(out, safe=False)


class SendReportPdfView(FormView):
    """Generating PDF report and sending email"""

    template_name = 'calculator/send_email.html'
    form_class = EmailRequestForm

    def form_valid(self, form):
        """1. Filtering product by date, retrieving email from user
           2. Generating PDF file, adding products and summary to the file
           3. Sending email"""

        email = form.cleaned_data.get('email')

        date = self.kwargs.get('date')

        products = Product.objects.filter(date=date)
        # summary = FullDayIntake.objects.filter(date=date)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawString(100, 800, f"Report for date: {date}")

        y_position = 750
        for product in products:
            c.drawString(100, y_position, f"Product: {product.name}, "
                                          f"kcal: {product.kcal}, "
                                          f"fat: {product.fat}, "
                                          f"carbs: {product.carbs}, "
                                          f"protein: {product.protein}")
            y_position -= 20

        # c.drawString(f'Total kcal: {summary.total_kcal},'
        #              f'Total fat: {summary.fat}, '
        #              f'Total carbs: {summary.carbs}, '
        #              f'Total protein: {summary.protein},'
        #
        #              )

        c.showPage()
        c.save()

        buffer.seek(0)

        email_subject = f"KetoApp report for {date}"
        email_body = "Please find attached the report in PDF format."
        email_message = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=DEFAULT_FROM_EMAIL,
            to=[email],
        )

        email_message.attach(f"report_{date}.pdf", buffer.getvalue(), 'application/pdf')
        email_message.send()

        return render(self.request, "calculator/send_email_success.html")


