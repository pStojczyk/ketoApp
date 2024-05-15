import datetime
from django.db import models
from django.db.models import Sum
from users.models import KetoAppUser


class Product(models.Model):
    date = models.DateField(default=datetime.date.today, blank=True)
    name = models.CharField(max_length=100, null=True, blank=False)
    grams = models.CharField(max_length=100, null=True, blank=False)
    kcal = models.PositiveIntegerField(null=True)
    carb = models.PositiveIntegerField(null=True)
    fat = models.PositiveIntegerField(null=True)
    protein = models.PositiveIntegerField(null=True)
    user = models.ManyToManyField(KetoAppUser, null=False)


class FullDayIntake(models.Model):
    date = models.DateField(null=False, blank=True)
    total_kcal = models.PositiveIntegerField(null=True)
    total_carbs = models.PositiveIntegerField(null=True)
    total_fat = models.PositiveIntegerField(null=True)
    total_protein = models.PositiveIntegerField(null=True)
    product = models.ManyToManyField(Product, null=False)
    user = models.ManyToManyField(KetoAppUser, null=False)

