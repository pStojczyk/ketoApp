"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from users.models import KetoAppUser
# , Demand)


class KetoAppUserModelTest(TestCase):
    """Test user models."""

    def setUp(self):
        """Test creating user for all tests."""
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_ketoappuser_is_created_by_signal(self):
        """Test creating KetoAppUser instance."""
        self.assertTrue(KetoAppUser.objects.filter(user=self.user).exists())


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
        keto_app_user = KetoAppUser.objects.create(
            weight=55,
            height=160,
            age=25,
            gender=KetoAppUser.GenderChoices.FEMALE,
            activity=KetoAppUser.ActivityChoices.MEDIUM,
        )
        expected_bmr = (9.99 * 55) + (6.25 * 160) - (4.92 * 25) - 161
        self.assertEqual(keto_app_user.expected_bmr(), expected_bmr)

#     def test_calculate_daily_cmp_inactive(self):
#         """Test creating CMP instance for inactive user."""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.INACTIVE
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         expected_cmp = bmr * 1.2
#         self.assertEqual(keto_app_user.calculate_daily_cmp(), expected_cmp)
#
#     def test_calculate_daily_cmp_very_high_activity(self):
#         """Test creating CMP instance for very high user activity."""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.VERY_HIGH
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         expected_cmp = bmr * 2.1
#         self.assertEqual(keto_app_user.calculate_daily_cmp(), expected_cmp)
#
#     def test_calculate_carbs_inactive(self):
#         """Test creating carbs instance for inactive user"""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.INACTIVE
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         cmp = bmr * 1.2
#         expected_carbs = (cmp * 0.05) // 4
#         self.assertEqual(keto_app_user.calculate_carbs(), expected_carbs)
#
#     def test_calculate_carbs_very_high_activity(self):
#         """Test creating carbs instance for very high user activity"""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.VERY_HIGH
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         cmp = bmr * 2.1
#         expected_carbs = (cmp * 0.05) // 4
#         self.assertEqual(keto_app_user.calculate_carbs(), expected_carbs)
#
#     def test_calculate_fat_inactive(self):
#         """Test creating fat instance for inactive user"""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.INACTIVE
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         cmp = bmr * 1.2
#         expected_fat = (cmp * 0.8) // 9
#         self.assertEqual(keto_app_user.calculate_fat(), expected_fat)
#
#     def test_calculate_fat_very_high_activity(self):
#         """Test creating fat instance for very high user activity"""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.VERY_HIGH
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         cmp = bmr * 2.1
#         expected_fat = (cmp * 0.8) // 9
#         self.assertEqual(keto_app_user.calculate_fat(), expected_fat)
#
#     def test_calculate_protein_inactive(self):
#         """Test creating protein instance for inactive user"""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.INACTIVE
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         cmp = bmr * 1.2
#         expected_protein = (cmp * 0.15) // 4
#         self.assertEqual(keto_app_user.calculate_protein(), expected_protein)
#
#     def test_calculate_protein_very_high_activity(self):
#         """Test creating protein instance for very high user activity"""
#         keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.VERY_HIGH
#         )
#         bmr = (9.99 * 70) + (6.25 * 175) - (4.92 * 30) + 5
#         cmp = bmr * 2.1
#         expected_protein = (cmp * 0.15) // 4
#         self.assertEqual(keto_app_user.calculate_protein(), expected_protein)
#
#
# class KetoAppUserDemandTest(TestCase):
#     """Test demand models."""
#
#     def setUp(self):
#         """Test creating user for all tests."""
#         self.user = User.objects.create_user(username='testuser', password='testpass123')
#         self.keto_app_user = KetoAppUser.objects.create(
#             user=self.user,
#             weight=70,
#             height=175,
#             age=30,
#             gender=KetoAppUser.GenderChoices.MALE,
#             activity=KetoAppUser.ActivityChoices.MEDIUM
#         )
#
#     def test_update_or_create_demand_creates_demand(self):
#         """Test if demand created"""
#         self.keto_app_user.update_or_create_demand()
#         demand = Demand.objects.get(keto_app_user=self.keto_app_user)
#         expected_cmp = self.keto_app_user.calculate_daily_cmp()
#         expected_fat = self.keto_app_user.calculate_fat()
#         expected_protein = self.keto_app_user.calculate_protein()
#         expected_carbs = self.keto_app_user.calculate_carbs()
#
#         self.assertEqual(demand.kcal, expected_cmp)
#         self.assertEqual(demand.fat, expected_fat)
#         self.assertEqual(demand.protein, expected_protein)
#         self.assertEqual(demand.carbs, expected_carbs)
#
#     def test_update_or_create_demand_updates_demand(self):
#         """Test if demand updated"""
#         Demand.objects.create(
#             keto_app_user=self.keto_app_user,
#             kcal=2000,
#             fat=100,
#             protein=150,
#             carbs=50
#         )
#
#         self.keto_app_user.update_or_create_demand()
#         demand = Demand.objects.get(keto_app_user=self.keto_app_user)
#         expected_cmp = self.keto_app_user.calculate_daily_cmp()
#         expected_fat = self.keto_app_user.calculate_fat()
#         expected_protein = self.keto_app_user.calculate_protein()
#         expected_carbs = self.keto_app_user.calculate_carbs()
#
#         self.assertEqual(demand.kcal, expected_cmp)
#         self.assertEqual(demand.fat, expected_fat)
#         self.assertEqual(demand.protein, expected_protein)
#         self.assertEqual(demand.carbs, expected_carbs)
#




