import datetime
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from .forms import CalendarForm, ProductRequestForm
from .models import FullDayIntake, Product
from .utils import GetConnection
from django.db.models import Sum

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

            return redirect("product_detail", pk=product_macronutrients.pk)

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


class CalendarView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        form = CalendarForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data.get('date')

            return redirect("products_list_by_date", date=date)

        return render(request, "calculator/calendar_form.html", {'form': form})

    def get(self, request, *args, **kwargs):
        form = CalendarForm(request.GET)
        return render(request, "calculator/calendar_form.html", {'form': form})


class ProductListByDateView(TemplateView):
    template_name = "calculator/list_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs.get('date')
        context['product_by_date'] = Product.objects.filter(date=context['date'])
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'calculator/delete_product_confirm.html'

    def get_success_url(self):
        if self.object.date == datetime.date.today():
            return reverse_lazy("profile")
        return reverse_lazy('products_list_by_date', args=[self.object.date])


class SummaryDetailView(LoginRequiredMixin, DetailView):
    model = FullDayIntake
    template_name = 'calculator/full_day_macronutrients.html'

    # def get_object(self, **kwargs):
    #     date = self.kwargs.get('date')
    #     products = Product.objects.filter(date=date)
    #     total_kcal = sum(product.kcal for product in products)
    #     total_fat = sum(product.fat for product in products)
    #     total_protein = sum(product.protein for product in products)
    #     total_carbs = sum(product.carb for product in products)
    #
    #     FullDayIntake.objects.update_or_create(
    #         date=date,
    #         defaults={
    #             'total_kcal': total_kcal,
    #             'total_carbs': total_carbs,
    #             'total_fat': total_fat,
    #             'total_protein': total_protein,
    #         })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.kwargs.get('date')
        products = Product.objects.filter(date=date)
        total_kcal = sum(product.kcal for product in products)
        total_fat = sum(product.fat for product in products)
        total_protein = sum(product.protein for product in products)
        total_carbs = sum(product.carb for product in products)

        FullDayIntake.objects.update_or_create(
            date=date,
            defaults={
                'total_kcal': total_kcal,
                'total_carbs': total_carbs,
                'total_fat': total_fat,
                'total_protein': total_protein,
            })

        context['date'] = date
        context['total_kcal'] = total_kcal
        context['total_carbs'] = total_carbs
        context['total_fat'] = total_fat
        context['total_protein'] = total_protein

        return context
    #





        # total = FullDayIntake.objects.update(
        #     {
        #         'total_kcal': total_kcal,
        #         'total_carbs': total_carbs,
        #         'total_fat': total_fat,
        #         'total_protein': total_protein,
        #     })

        # return redirect('summary_detail', pk=total.pk)


# def sum_all_products_nutrients():
#     queryset = Product.objects.filter(date=datetime.date.today())
#     total_kcal = queryset.aggregate(Sum("kcal"))
#     total_fat = queryset.aggregate(Sum("fat"))
#     total_protein = queryset.aggregate(Sum("protein"))
#     total_carbs = queryset.aggregate(Sum("carb"))

    # products = Product.objects.filter(date=datetime.date.today())
    # total_kcal = sum(product.kcal for product in products)
    # total_fat = sum(product.fat for product in products)
    # total_protein = sum(product.protein for product in products)
    # total_carbs = sum(product.carb for product in products)

    # total = FullDayIntake.objects.update_or_create(
    #         date=datetime.date.today(),
    #         defaults={
    #             'total_kcal': total_kcal,
    #             'total_carbs': total_carbs,
    #             'total_fat': total_fat,
    #             'total_protein': total_protein,
    #         })
    # return redirect('full_day_macronutrients', pk=total.pk)
    #
    #
    #
