"""
Tests for models.
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from calculator.models import Product, FullDayIntake
from users.models import KetoAppUser


class ProductModelTest(TestCase):
    """Test calculator models."""

    def setUp(self):
        """Test create KetoAppUser for all tests."""

        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.keto_app_user = self.user.ketoappuser

    def test_update_or_create_fulldayintake_creates_new_fulldayintake(self):
        """Test create products for new FullDayIntake"""

        product1 = Product.objects.create(
            date=datetime.date.today(),
            name="Egg",
            grams="100",
            kcal=155,
            carb=1,
            fat=11,
            protein=13,
        )
        product1.user.add(self.keto_app_user)

        product2 = Product.objects.create(
            date=datetime.date.today(),
            name="Chicken",
            grams="150",
            kcal=239,
            carb=0,
            fat=14,
            protein=27,
        )
        product2.user.add(self.keto_app_user)

        product1.update_or_create_fulldayintake()

        fulldayintake = FullDayIntake.objects.get(date=datetime.date.today())

        self.assertEqual(fulldayintake.total_kcal, 394)
        self.assertEqual(fulldayintake.total_fat, 25)
        self.assertEqual(fulldayintake.total_protein, 40)
        self.assertEqual(fulldayintake.total_carbs, 1)

    def test_update_or_create_fulldayintake_updates_existing_fulldayintake(self):
        """Test create FullDayIntake with existing today's date"""

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
        product.user.add(self.keto_app_user)

        product.update_or_create_fulldayintake()

        fulldayintake = FullDayIntake.objects.get(date=datetime.date.today())

        self.assertEqual(fulldayintake.total_kcal, 160)
        self.assertEqual(fulldayintake.total_fat, 15)
        self.assertEqual(fulldayintake.total_protein, 2)
        self.assertEqual(fulldayintake.total_carbs, 8)

    def test_update_or_create_fulldayintake_0_values(self):
        """Test FullDayIntake creates with 0 values for nutritional fields"""
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
        product.user.add(self.user.ketoappuser)

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
        product.user.add(self.user.ketoappuser)

        product.update_or_create_fulldayintake()

        fulldayintake = FullDayIntake.objects.get(date=datetime.date.today())

        self.assertEqual(fulldayintake.total_kcal, 0)
        self.assertEqual(fulldayintake.total_fat, 0)
        self.assertEqual(fulldayintake.total_protein, 0)
        self.assertEqual(fulldayintake.total_carbs, 0)


class FullDayIntakeModelTest(TestCase):

    def setUp(self):
        """Creating configuration for all tests"""
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.product1 = Product.objects.create(
            date=datetime.date.today(),
            name="Egg",
            grams="100",
            kcal=155,
            carb=1,
            fat=11,
            protein=13,
        )

        self.product2 = Product.objects.create(
            date=datetime.date.today(),
            name="Chicken Breast",
            grams="150",
            kcal=165,
            carb=0,
            fat=3,
            protein=31,
        )

        self.product1.user.add(self.user.ketoappuser)
        self.product2.user.add(self.user.ketoappuser)

    def test_fulldayintake_creation(self):
        """Test creating FullDayIntake with valid data"""
        fulldayintake = FullDayIntake.objects.create(
            date=datetime.date.today(),
            total_kcal=320,
            total_carbs=1,
            total_fat=14,
            total_protein=44,
            start=datetime.date.today(),
            user=self.user.ketoappuser
        )

        fulldayintake.product.set([self.product1, self.product2])

        self.assertEqual(fulldayintake.total_kcal, 320)
        self.assertEqual(fulldayintake.total_carbs, 1)
        self.assertEqual(fulldayintake.total_fat, 14)
        self.assertEqual(fulldayintake.total_protein, 44)
        self.assertEqual(fulldayintake.date, datetime.date.today())
        self.assertIn(self.product1, fulldayintake.product.all())
        self.assertIn(self.product2, fulldayintake.product.all())

    def test_fulldayintake_relation_with_products(self):
        """Test the ManyToMany relation between FullDayIntake and Product"""
        fulldayintake = FullDayIntake.objects.create(
            date=datetime.date.today(),
            total_kcal=320,
            total_carbs=1,
            total_fat=14,
            total_protein=44,
        )

        fulldayintake.product.set([self.product1, self.product2])

        self.assertEqual(fulldayintake.product.count(), 2)
        self.assertIn(self.product1, fulldayintake.product.all())
        self.assertIn(self.product2, fulldayintake.product.all())

    def test_fulldayintake_relation_with_users(self):
        """Test the ManyToMany relation between FullDayIntake and KetoAppUser"""
        fulldayintake = FullDayIntake.objects.create(
            date=datetime.date.today(),
            total_kcal=320,
            total_carbs=1,
            total_fat=14,
            total_protein=44,
            user=self.user.ketoappuser
        )

        self.assertEqual(fulldayintake.user, self.user.ketoappuser)
