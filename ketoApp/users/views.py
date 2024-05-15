import datetime
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from .models import Demand, KetoAppUser
from calculator.models import Product


class Register(CreateView):

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"You have been successfully signed up {username} !")
            return redirect('login')

        return render(request, 'users/register.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, "users/register.html", {"form": form})


class Profile(LoginRequiredMixin, TemplateView):
    model = Product
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['today'] = datetime.date.today()
        ctx['products_list'] = Product.objects.filter(date=ctx['today'])

        return ctx


class KetoAppUserUpdateView(UpdateView):
    model = KetoAppUser
    fields = ['weight', 'height', 'age', 'gender', 'activity']
    template_name = 'users/keto_app_user_form.html'

    def get_success_url(self):
        return reverse_lazy('keto_app_user_demand_detail', args=[self.get_object().demand.id])


class DemandDetailView(DetailView):
    model = Demand
    template_name = 'users/daily-requirements.html'

