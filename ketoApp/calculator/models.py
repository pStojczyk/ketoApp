"""
Database models for storing user dietary information and daily summaries.
"""

import datetime

from django.db import models
from django.db.models import Sum

from users.models import KetoAppUser


class Product(models.Model):
    """Model representing a food product with macronutrient data and consumption details."""

    date = models.DateField(default=datetime.date.today, blank=True)
    name = models.CharField(max_length=100, null=True, blank=False)
    grams = models.PositiveIntegerField(null=True, blank=False)
    kcal = models.PositiveIntegerField(null=True)
    carb = models.PositiveIntegerField(null=True)
    fat = models.PositiveIntegerField(null=True)
    protein = models.PositiveIntegerField(null=True)
    user = models.ManyToManyField(KetoAppUser, null=False)

    def update_or_create_fulldayintake(self):
        """Method aggregates macronutrient totals for the day and updates or creates a corresponding
        FullDayIntake instance."""

        totals = Product.objects.filter(date=self.date).aggregate(
            total_kcal=Sum("kcal"),
            total_fat=Sum("fat"),
            total_protein=Sum("protein"),
            total_carbs=Sum("carb"),
        )

        total_kcal = totals['total_kcal'] or 0
        total_fat = totals['total_fat'] or 0
        total_protein = totals['total_protein'] or 0
        total_carbs = totals['total_carbs'] or 0

        obj, created = FullDayIntake.objects.update_or_create(
                date=self.date,
                defaults={
                    'total_kcal': total_kcal,
                    'total_carbs': total_carbs,
                    'total_fat': total_fat,
                    'total_protein': total_protein,
                    'user': self.user.first(),
                })


class FullDayIntake(models.Model):
    """Model representing the daily summary of total macronutrients consumed."""
    date = models.DateField(null=True, blank=True)
    total_kcal = models.PositiveIntegerField(null=True)
    total_carbs = models.PositiveIntegerField(null=True)
    total_fat = models.PositiveIntegerField(null=True)
    total_protein = models.PositiveIntegerField(null=True)
    product = models.ManyToManyField(Product, null=False)
    user = models.ForeignKey(KetoAppUser, on_delete=models.CASCADE, null=True)
    start = models.DateField(null=True, blank=True)
