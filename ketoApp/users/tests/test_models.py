"""
Tests for user.models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from users.models import KetoAppUser, Demand


class KetoAppUserModelTest(TestCase):
    """Test user models."""

    def setUp(self):
        """Test creating user for all tests."""
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_ketoappuser_is_created_by_signal(self):
        """Test creating KetoAppUser instance."""
        self.assertTrue(KetoAppUser.objects.filter(user=self.user).exists())

    def test_token_is_created_by_signal(self):
        """Test creating Token instance while creating User."""
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_calculate_bmr_male(self):
        """Test creating BMR instance for male."""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.LOW,
        )
        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_bmr = 1650.45
        self.assertEqual(keto_app_user.calculate_bmr(), expected_bmr)

    def test_calculate_bmr_female(self):
        """Test creating BMR instance for female."""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=55,
            height=160,
            age=25,
            gender=KetoAppUser.GenderChoices.FEMALE,
            activity=KetoAppUser.ActivityChoices.MEDIUM,
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_bmr = 1265.45

        self.assertEqual(keto_app_user.calculate_bmr(), expected_bmr)

    def test_calculate_daily_cmp_inactive(self):
        """Test creating CMP instance for inactive user."""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.INACTIVE
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_cmp = 1980

        self.assertEqual(keto_app_user.calculate_daily_cmp(), expected_cmp)

    def test_calculate_daily_cmp_very_high_activity(self):
        """Test creating CMP instance for very high user activity."""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.VERY_HIGH
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_cmp = 3465

        self.assertEqual(keto_app_user.calculate_daily_cmp(), expected_cmp)

    def test_calculate_carbs_inactive(self):
        """Test creating carbs instance for inactive user"""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.INACTIVE
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_carbs = 24.0

        self.assertEqual(keto_app_user.calculate_carbs(), expected_carbs)

    def test_calculate_carbs_very_high_activity(self):
        """Test creating carbs instance for very high user activity"""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.VERY_HIGH
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_carbs = 43.0

        self.assertEqual(keto_app_user.calculate_carbs(), expected_carbs)

    def test_calculate_fat_inactive(self):
        """Test creating fat instance for inactive user"""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.INACTIVE
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_fat = 176.0

        self.assertEqual(keto_app_user.calculate_fat(), expected_fat)

    def test_calculate_fat_very_high_activity(self):
        """Test creating fat instance for very high user activity"""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.VERY_HIGH
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_fat = 308.0

        self.assertEqual(keto_app_user.calculate_fat(), expected_fat)

    def test_calculate_protein_inactive(self):
        """Test creating protein instance for inactive user"""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.INACTIVE
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_protein = 74.0

        self.assertEqual(keto_app_user.calculate_protein(), expected_protein)

    def test_calculate_protein_very_high_activity(self):
        """Test creating protein instance for very high user activity"""
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.VERY_HIGH
        )

        keto_app_user = KetoAppUser.objects.get(user=self.user)

        expected_protein = 129.0

        self.assertEqual(keto_app_user.calculate_protein(), expected_protein)


class KetoAppUserDemandTest(TestCase):
    """Test demand models."""

    def setUp(self):
        """Test creating user for all tests."""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        KetoAppUser.objects.filter(user=self.user).update(
            weight=70,
            height=175,
            age=30,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.MEDIUM
        )
        self.keto_app_user = KetoAppUser.objects.get(user=self.user)

    def test_update_or_create_demand_creates_demand(self):
        """Test if demand created"""

        expected_cmp = self.keto_app_user.calculate_daily_cmp()
        expected_fat = self.keto_app_user.calculate_fat()
        expected_protein = self.keto_app_user.calculate_protein()
        expected_carbs = self.keto_app_user.calculate_carbs()

        self.keto_app_user.update_or_create_demand()
        demand = Demand.objects.get(keto_app_user=self.keto_app_user)

        self.assertEqual(demand.kcal, expected_cmp)
        self.assertEqual(demand.fat, expected_fat)
        self.assertEqual(demand.protein, expected_protein)
        self.assertEqual(demand.carbs, expected_carbs)




