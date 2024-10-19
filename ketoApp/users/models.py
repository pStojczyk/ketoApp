from django.contrib.auth.models import User
from django.db import models


class KetoAppUser(models.Model):
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

    """Dzienne minimalne zapotrzebowanie kaloryczne BMR dla uzytkownika"""

    def calculate_bmr(self):
        if self.gender == 'Male':
            bmr = (9.99 * int(self.weight)) + (6.25 * int(self.height)) - (4.92 * int(self.age)) + 5
        elif self.gender == 'Female':
            bmr = (9.99 * int(self.weight)) + (6.25 * int(self.height)) - (4.92 * int(self.age)) - 161

        return round(bmr, 2)

    """Całkowita dzienna przemiana materii uzytkownika"""

    def calculate_daily_cmp(self):
        activity_values = {'inactive': 1.2,
                           'low': 1.4,
                           'medium': 1.6,
                           'high': 1.8,
                           'very_high': 2.1}

        if self.activity in activity_values:
            activity_value = activity_values[self.activity]
            cmp_result = self.calculate_bmr() * activity_value

            return int(cmp_result)

    """Dzienne zapotrzebowanie na makro"""

    def calculate_carbs(self):
        return self.calculate_daily_cmp() * 0.05 // 4

    def calculate_fat(self):
        return self.calculate_daily_cmp() * 0.8 // 9

    def calculate_protein(self):
        return self.calculate_daily_cmp() * 0.15 // 4

    def update_or_create_demand(self):
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
    keto_app_user = models.OneToOneField(KetoAppUser, on_delete=models.CASCADE)
    kcal = models.PositiveIntegerField(null=True)
    fat = models.PositiveIntegerField(null=True)
    protein = models.PositiveIntegerField(null=True)
    carbs = models.PositiveIntegerField(null=True)

