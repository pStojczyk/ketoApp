import datetime
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, TemplateView

from .forms import ProductRequestForm
from .models import FullDayIntake, Product
from .utils import GetConnection


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


# class RemoveEventView(View):
#     def get(self, request):
#         id = request.GET.get("id")
#         event = FullDayIntake.objects.get(id=id)
#         event.delete()
#         data = {}
#
#         return JsonResponse(data)
