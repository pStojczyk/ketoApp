"""
Models for user and dietary demand in KetoApp.
"""

from django.contrib.auth.models import User
from django.db import models


class KetoAppUser(models.Model):
    """
    This model contains fields for user attributes such as weight, height, age, gender, and activity level.
    It includes methods to calculate basal metabolic rate (BMR), daily calorie requirements (CMP),
    and recommended daily intake of macronutrients (carbs, fat, protein) based on user details.
    """

    class GenderChoices(models.TextChoices):
        MALE = 'Male',
        FEMALE = 'Female'

    class ActivityChoices(models.TextChoices):
        INACTIVE = ('inactive', 'inactivity, sedentary work')
        LOW = ('low', 'low activity, sedentary work and 1-2 workouts a week')
        MEDIUM = ('medium', 'medium activity, sedentary work and workouts 3-4 times a week')
        HIGH = ('high', 'high activity, physical work and 3-4 workouts a week')
        VERY_HIGH = ('very_high', 'very high activity, professional athletes, people who train every day')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(null=True)
    height = models.PositiveIntegerField(null=True)
    age = models.PositiveIntegerField(null=True)
    gender = models.CharField(max_length=32, null=True, choices=GenderChoices.choices)
    activity = models.CharField(max_length=100, null=True, choices=ActivityChoices.choices)

    def calculate_bmr(self):
        """
        Calculate the Basal Metabolic Rate (BMR) for the user based on weight, height, age, and gender.

        Returns:
            float: The BMR value, representing minimum daily caloric needs.
        """

        if self.gender == 'Male':
            bmr = (9.99 * int(self.weight)) + (6.25 * int(self.height)) - (4.92 * int(self.age)) + 5
        elif self.gender == 'Female':
            bmr = (9.99 * int(self.weight)) + (6.25 * int(self.height)) - (4.92 * int(self.age)) - 161
        else:
            raise ValueError("Invalid gender value.")

        return round(bmr, 2)

    def calculate_daily_cmp(self):
        """
        Calculate the user's Total Metabolic Rate based on activity level.
        This method multiplies the user's BMR by an activity specific to their activity level.

        Returns:
            int: The CMP value, representing the total daily caloric needs based on activity level.
        """

        activity_values = {'inactive': 1.2,
                           'low': 1.4,
                           'medium': 1.6,
                           'high': 1.8,
                           'very_high': 2.1}

        if self.activity in activity_values:
            activity_value = activity_values[self.activity]
            cmp_result = self.calculate_bmr() * activity_value

            return int(cmp_result)

    def calculate_carbs(self):
        """
        Calculate the recommended daily intake of carbohydrates in grams.

        Returns:
            float: Daily grams of carbohydrates based on 5% of the CMP.
        """

        return self.calculate_daily_cmp() * 0.05 // 4

    def calculate_fat(self):
        """
        Calculate the recommended daily intake of fats in grams.

        Returns:
            float: Daily grams of fats based on 80% of the CMP.
        """

        return self.calculate_daily_cmp() * 0.8 // 9

    def calculate_protein(self):
        """
        Calculate the recommended daily intake of proteins in grams.

        Returns:
            float: Daily grams of proteins based on 15% of the CMP.
        """

        return self.calculate_daily_cmp() * 0.15 // 4

    def update_or_create_demand(self):
        """
        Update or create a Demand record with calculated dietary requirements and stores the values
        in the associated Demand model.
        """

        cmp = self.calculate_daily_cmp()
        fat = self.calculate_fat()
        protein = self.calculate_protein()
        carbs = self.calculate_carbs()

        Demand.objects.update_or_create(
            keto_app_user=self,
            defaults={
                'kcal': cmp,
                'fat': fat,
                'protein': protein,
                'carbs': carbs,
            })


class Demand(models.Model):
    """
    Model to store calculated dietary requirements for a user in KetoApp.

    Fields include daily calorie intake (kcal), fats, proteins, and carbohydrates, based on the user's profile.
    Each `Demand` record is associated with a unique `KetoAppUser` instance.
    """

    keto_app_user = models.OneToOneField(KetoAppUser, on_delete=models.CASCADE)
    kcal = models.PositiveIntegerField(null=True, blank=False)
    fat = models.PositiveIntegerField(null=True, blank=False)
    protein = models.PositiveIntegerField(null=True, blank=False)
    carbs = models.PositiveIntegerField(null=True, blank=False)

