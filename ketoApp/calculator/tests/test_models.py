"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth.models import User
import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import Product, FullDayIntake
from users.models import KetoAppUser


class ProductModelTest(TestCase):
    """Test calculator models."""

    def setUp(self):
        """Test create KetoAppUser for all tests."""

        self.user = KetoAppUser.objects.create_user(username='testuser', password='testpassword123')

    def test_update_or_create_fulldayintake_creates_new_fulldayintake(self):
        """Test create products for new fulldayintake"""

        product1 = Product.objects.create(
            date=datetime.date.today(),
            name="Egg",
            grams="100",
            kcal=155,
            carb=1,
            fat=11,
            protein=13,
        )
        product1.user.add(self.user)

        product2 = Product.objects.create(
            date=datetime.date.today(),
            name="Chicken",
            grams="150",
            kcal=239,
            carb=0,
            fat=14,
            protein=27,
        )
        product2.user.add(self.user)

        product1.update_or_create_fulldayintake()

        fulldayintake = FullDayIntake.objects.get(date=datetime.date.today())

        self.assertEqual(fulldayintake.total_kcal, 394)
        self.assertEqual(fulldayintake.total_fat, 25)
        self.assertEqual(fulldayintake.total_protein, 40)
        self.assertEqual(fulldayintake.total_carbs, 1)

    def test_update_or_create_fulldayintake_updates_existing_fulldayintake(self):
        """Test create fulldayintake with existing today's date"""

        FullDayIntake.objects.create(
            date=datetime.date.today(),
            total_kcal=200,
            total_carbs=20,
            total_fat=10,
            total_protein=15
        )

        product = Product.objects.create(
            date=datetime.date.today(),
            name="Avocado",
            grams="100",
            kcal=160,
            carb=8,
            fat=15,
            protein=2,
        )
        product.user.add(self.user)

        product.update_or_create_fulldayintake()

        fulldayintake = FullDayIntake.objects.get(date=datetime.date.today())

        self.assertEqual(fulldayintake.total_kcal, 360)
        self.assertEqual(fulldayintake.total_fat, 25)
        self.assertEqual(fulldayintake.total_protein, 17)
        self.assertEqual(fulldayintake.total_carbs, 28)

    def test_update_or_create_fulldayintake_0_values(self):
        """Test fulldayintake creates with 0 values for nutritional fields"""
        Product.objects.all().delete()

        product = Product.objects.create(
            date=datetime.date.today(),
            name="Water",
            grams="1000",
            kcal=0,
            carb=0,
            fat=0,
            protein=0,
        )
        product.user.add(self.user)

        product.update_or_create_fulldayintake()

        fulldayintake = FullDayIntake.objects.get(date=datetime.date.today())

        self.assertEqual(fulldayintake.total_kcal, 0)
        self.assertEqual(fulldayintake.total_fat, 0)
        self.assertEqual(fulldayintake.total_protein, 0)
        self.assertEqual(fulldayintake.total_carbs, 0)

    def test_update_or_create_fulldayintake_with_None_values(self):
        """Test creating product with None values for nutritional fields"""

        product = Product.objects.create(
            date=datetime.date.today(),
            name=None,
            grams=None,
            kcal=None,
            carb=None,
            fat=None,
            protein=None,
        )
        product.user.add(self.user)

        product.update_or_create_fulldayintake()

        fulldayintake = FullDayIntake.objects.get(date=datetime.date.today())

        self.assertEqual(fulldayintake.total_kcal, 0)
        self.assertEqual(fulldayintake.total_fat, 0)
        self.assertEqual(fulldayintake.total_protein, 0)
        self.assertEqual(fulldayintake.total_carbs, 0)