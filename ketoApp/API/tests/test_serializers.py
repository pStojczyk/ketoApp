"""
Test suite for the serializers in the API module of the Django application.
"""
from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from API.serializers import DemandSerializer, FullDayIntakeSerializer, ParameterSerializer, ProductSerializer
from calculator.models import FullDayIntake, Product
from users.models import Demand, KetoAppUser


class TestProductSerializer(APITestCase):
    """
    Test for the ProductSerializer includes tests for creating, updating and serializing Product instances.
    """

    @patch('calculator.utils.GetConnection.get_connection')
    def test_create_serializer_valid(self, mock_get_connection):
        """
        Test the creation of a Product instance using the mocks of the external API to retrieve data and
        verifies correct assignment of calculated fields (e.g., kcal, carb, fat, protein).
        """
        mock_get_connection.return_value = {
            'calories': 100,
            'totalNutrients': {
                'CHOCDF': {'quantity': 20},
                'FAT': {'quantity': 5},
                'PROCNT': {'quantity': 10}
            }
        }
        data = {
            'name': 'apple',
            'grams': 100
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        product = serializer.save()
        self.assertEqual(product.name, 'apple')
        self.assertEqual(product.kcal, 100)
        self.assertEqual(product.carb, 20)
        self.assertEqual(product.fat, 5)
        self.assertEqual(product.protein, 10)
        self.assertEqual(product.grams, 100)

    @patch('calculator.utils.GetConnection.get_connection')
    def test_update_serializer(self, mock_get_connection):
        """
        Test the update of a Product instance using the mocks of the external API to retrieve data and
        verifies correct assignment of calculated fields (e.g., kcal, carb, fat, protein).
        """
        mock_get_connection.return_value = {
            'calories': 120,
            'totalNutrients': {
                'CHOCDF': {'quantity': 25},
                'FAT': {'quantity': 7},
                'PROCNT': {'quantity': 12}
            }
        }
        product = Product.objects.create(
            name='apple', grams=100, kcal=100, carb=20, fat=5, protein=10
        )
        data = {'grams': 150}
        serializer = ProductSerializer(instance=product, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_product = serializer.save()
        self.assertEqual(updated_product.grams, 150)
        self.assertEqual(updated_product.kcal, 120)
        self.assertEqual(updated_product.carb, 25)

    def test_to_representation(self):
        """
        Test the `to_representation` method of the serializer verifies the custom message included
        in the serialized output for a Product instance.
        """
        product = Product(
            name='apple', grams=100, kcal=100, carb=20, fat=5, protein=10, date=date.today()
        )
        serializer = ProductSerializer(product)
        representation = serializer.data
        self.assertIn('message', representation)
        self.assertEqual(representation['message'], f"Product apple created successfully!")


class TestParameterSerializer(APITestCase):
    """
    Test suite for the ParameterSerializer and verifies:
    - Retrieval of data using the serializer.
    - Updating of `KetoAppUser` instances using the serializer.
    """

    def setUp(self):
        """
        Set up creates a `User` instance and configures related `KetoAppUser` fields
        such as weight, height, age, gender, and activity level for testing purposes.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.keto_user = KetoAppUser.objects.get(user=self.user)

        self.keto_user.weight = 70
        self.keto_user.height = 175
        self.keto_user.age = 30
        self.keto_user.gender = 'Male'
        self.keto_user.activity = 'medium'
        self.keto_user.save()

    def test_serializer_retrieve(self):
        """
        Test the retrieval of a `KetoAppUser` instance via the serializer and ensures that
        the serializer correctly outputs the fields of a `KetoAppUser` instance.
        """
        serializer = ParameterSerializer(instance=self.keto_user)
        data = serializer.data
        self.assertEqual(data['weight'], 70)
        self.assertEqual(data['height'], 175)
        self.assertEqual(data['age'], 30)
        self.assertEqual(data['gender'], 'Male')
        self.assertEqual(data['activity'], 'medium')

    def test_serializer_update(self):
        """
        Test the update functionality of the serializer for a `KetoAppUser` instance.
        This test verifies that:
        - The serializer validates the  data.
        - The `KetoAppUser` instance is correctly updated with the provided values.
        """
        data = {
            'weight': 75,
            'height': 180,
            'age': 31,
            'gender': 'Male',
            'activity': 'high'
        }
        serializer = ParameterSerializer(instance=self.keto_user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.weight, 75)
        self.assertEqual(updated_user.height, 180)
        self.assertEqual(updated_user.age, 31)
        self.assertEqual(updated_user.gender, 'Male')
        self.assertEqual(updated_user.activity, 'high')


class DemandSerializerTest(APITestCase):
    """
    Test for the DemandSerializer verifies:
    - Serialization of `Demand` instances.
    - Deserialization of valid data into `Demand` instances.
    - Validation of invalid data during deserialization.
    """

    def setUp(self):
        """
        Set up a test user, associated `KetoAppUser` and `Demand` instance.
        - `User` instance for authentication purposes.
        - Corresponding `KetoAppUser` instance created automatically by signals.
        - `Demand` instance associated with the `KetoAppUser` to test the serializer.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.keto_user = KetoAppUser.objects.get(user=self.user)

        self.demand = Demand.objects.create(
            keto_app_user=self.keto_user,
            kcal=2000,
            fat=70,
            protein=150,
            carbs=250
        )

    def test_demand_serializer_serialization(self):
        """
        Test the serialization of a `Demand` instance ensures that the serializer correctly converts
        a `Demand` instance into a dictionary containing data.
        """
        serializer = DemandSerializer(instance=self.demand)
        data = serializer.data

        self.assertEqual(data['id'], self.demand.id)
        self.assertEqual(data['keto_app_user'], self.keto_user.id)
        self.assertEqual(data['kcal'], 2000)
        self.assertEqual(data['fat'], 70)
        self.assertEqual(data['protein'], 150)
        self.assertEqual(data['carbs'], 250)

    def test_demand_serializer_deserialization_valid(self):
        """
        Test the deserialization of valid data into a `Demand` instance ensures that:
        - Valid input data is correctly validated by the serializer.
        - The validated data matches the input data.
        """
        valid_data = {
            'keto_app_user': self.keto_user.id,
            'kcal': 2200,
            'fat': 80,
            'protein': 160,
            'carbs': 300
        }
        serializer = DemandSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['kcal'], 2200)

    def test_demand_serializer_deserialization_invalid(self):
        """
        Test the deserialization of invalid data checks the serializer's behavior when provided with incomplete data.
        It ensures that:
        - Validation fails for missing required fields.
        - Error messages are returned for the missing fields.
        """
        invalid_data = {'fat': 70}

        serializer = DemandSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('kcal', serializer.errors)
        self.assertIn('protein', serializer.errors)
        self.assertIn('carbs', serializer.errors)


class FullDayIntakeSerializerTest(APITestCase):
    def setUp(self):
        """Create an instance of FullDayIntake and a user for testing."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.full_day_intake = FullDayIntake.objects.create(
            date=date(2025, 1, 1),
            total_kcal=2000,
            total_fat=70,
            total_protein=150,
            total_carbs=250,
            user=self.user.ketoappuser
        )
        self.serializer = FullDayIntakeSerializer(instance=self.full_day_intake)

    def test_serializer_fields(self):
        """Test that the serializer contains the appropriate fields."""
        data = self.serializer.data
        self.assertIn('title', data)
        self.assertIn('start', data)
        self.assertIn('url', data)
        self.assertIn('details', data)

    def test_get_title(self):
        """Test the get_title method in the serializer."""
        expected_title = (
            'TOTAL KCAL: 2000'
        )
        self.assertEqual(self.serializer.get_title(self.full_day_intake), expected_title)

    def test_get_url(self):
        """Test the get_url method in the serializer."""
        expected_url = reverse('products_list_by_date', args=[self.full_day_intake.date])
        self.assertEqual(self.serializer.get_url(self.full_day_intake), expected_url)

    def test_serializer_output(self):
        """Test the complete output of the serializer."""
        expected_output = {
            'title': 'TOTAL KCAL: 2000',
            'start': '2025-01-01',
            'url': reverse('products_list_by_date', args=[self.full_day_intake.date]),
            'details': 'TOTAL FAT: 70,\nTOTAL PROTEIN: 150,\nTOTAL CARBS: 250',
        }

        self.assertEqual(self.serializer.data, expected_output)
