"""
Test for the API ViewSets related to the calculator and user management modules in the Django application.
"""
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from API.serializers import FullDayIntakeSerializer
from calculator.models import FullDayIntake, Product
from users.models import Demand, KetoAppUser


class TestProductViewSet(APITestCase):
    """
    Test for the Product API ViewSet, covering the main CRUD operations
    and filtering for the Product model.
    """
    def setUp(self):
        """
        Set up a user, client and token for the tests.
        This method is called before each test method.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.token = Token.objects.get(user=self.user)
        self.client = APIClient()

    @patch('calculator.utils.GetConnection.get_connection')
    def test_create_product(self, mock_get_connection):
        """
        Test the creation of a new product. This includes mocking the
        external API connection to simulate nutrient data retrieval.
        """
        mock_get_connection.return_value = {
            'calories': 100,
            'totalNutrients': {
                'CHOCDF': {'quantity': 20},
                'FAT': {'quantity': 5},
                'PROCNT': {'quantity': 10}
            }
        }

        product_data = {'name': 'apple', 'grams': 100}
        url = f"{reverse('products-list')}?token={self.token.key}"
        response = self.client.post(url, data=product_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'apple')

    @patch('calculator.utils.GetConnection.get_connection')
    def test_update_product(self, mock_get_connection):
        """
        Test updating an existing product's attributes. This includes
        mocking the external API call for nutrient data retrieval.
        """
        mock_get_connection.return_value = {
            'calories': 120,
            'totalNutrients': {
                'CHOCDF': {'quantity': 25},
                'FAT': {'quantity': 7},
                'PROCNT': {'quantity': 12}
            }
        }
        product = Product.objects.create(name='apple', grams=100, kcal=100, carb=20, fat=5, protein=10)
        update_data = {'grams': 150}
        url = f"{reverse('products-detail', kwargs={'pk': product.id})}?token={self.token.key}"
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['grams'], 150)

    def test_list_products(self):
        """
        Test retrieving the list of products. This checks if multiple products
        can be created and listed successfully.
        """
        Product.objects.create(name='apple', grams=100, kcal=100, carb=20, fat=5, protein=10)
        Product.objects.create(name='banana', grams=150, kcal=150, carb=30, fat=1, protein=3)
        self.products_list_url = f"{reverse('products-list')}?token={self.token.key}"
        response = self.client.get(self.products_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_delete_product(self):
        """
        Test deleting an existing product. This verifies that the product
        is successfully removed from the database after deletion.
        """
        product = Product.objects.create(name='apple', grams=100, kcal=100, carb=20, fat=5, protein=10)
        url = f"{reverse('products-detail', kwargs={'pk': product.id})}?token={self.token.key}"
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_filter_products_by_name(self):
        """
        Test filtering products by name. This checks if products can be
        filtered correctly based on the provided query parameter.
        Two products are created, and the response is validated to ensure
        only the correct product is returned.
        """
        Product.objects.create(name='apple', grams=100, kcal=100, carb=20, fat=5, protein=10)
        Product.objects.create(name='banana', grams=150, kcal=150, carb=30, fat=1, protein=3)

        self.products_list_url = f"{reverse('products-list')}?token={self.token.key}"
        response = self.client.get(f"{self.products_list_url}&name=apple")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'apple')

    def test_ordering_products_by_date(self):
        """
        Test ordering products by their creation date. This checks if the
        API correctly orders the products based on the specified query parameter.
        Two products with different creation dates are created and verified
        to ensure the order in the response is correct.
        """
        Product.objects.create(name='apple', grams=100, kcal=100, carb=20, fat=5, protein=10, date='2024-12-01')
        Product.objects.create(name='banana', grams=150, kcal=150, carb=30, fat=1, protein=3, date='2024-12-02')

        self.products_list_url = f"{reverse('products-list')}?token={self.token.key}"
        response = self.client.get(f"{self.products_list_url}&ordering=-date")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['name'], 'banana')


class TestPersonalParametersViewSet(APITestCase):
    """
    Test for the Personal Parameters API ViewSet, covering the retrieval
    and updating of personal parameters for authenticated users.
    """
    def setUp(self):
        """
        Set up a user, token, and authenticate the API client.
        This method is called before each test method to ensure a clean state.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.token = Token.objects.get(user=self.user)
        self.client = APIClient()

    def test_retrieve_personal_parameters(self):
        """
        Test retrieving the personal parameters of the authenticated user.
        This test checks if the personal parameters for the user are retrieved correctly
        from the API after they have been set. It verifies that the returned data matches
        the expected values for weight, height, age, gender, and activity level.
        """

        keto_user = self.user.ketoappuser
        keto_user.weight = 70
        keto_user.height = 175
        keto_user.age = 30
        keto_user.gender = 'Male'
        keto_user.activity = 'medium'
        keto_user.save()

        keto_user = KetoAppUser.objects.get(user=self.user)
        self.assertIsNotNone(keto_user)

        url = f"{reverse('personal-parameters-detail', kwargs={'pk': keto_user.id})}?token={self.token.key}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['weight'], 70)
        self.assertEqual(response.data['height'], 175)
        self.assertEqual(response.data['age'], 30)
        self.assertEqual(response.data['gender'], 'Male')
        self.assertEqual(response.data['activity'], 'medium')

    def test_update_personal_parameters(self):
        """
        Test updating the personal parameters of the authenticated user.
        This test verifies that the personal parameters can be updated successfully
        through the API. It checks if the new values are correctly saved in the
        database after the update request and that the response status is 200 OK.
        """

        keto_user = self.user.ketoappuser
        keto_user.weight = 70
        keto_user.height = 175
        keto_user.age = 30
        keto_user.gender = 'Male'
        keto_user.activity = 'medium'
        keto_user.save()

        updated_data = {
            'weight': 75,
            'height': 180,
            'age': 31,
            'gender': 'Male',
            'activity': 'high'
        }

        url = f"{reverse('personal-parameters-detail', kwargs={'pk': keto_user.id})}?token={self.token.key}"
        response = self.client.put(url, data=updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        keto_user.refresh_from_db()
        self.assertEqual(keto_user.weight, 75)
        self.assertEqual(keto_user.height, 180)
        self.assertEqual(keto_user.age, 31)
        self.assertEqual(keto_user.gender, 'Male')
        self.assertEqual(keto_user.activity, 'high')


class DemandDetailViewSetTest(APITestCase):
    """
    Test suite for the DemandDetailViewSet, covering the retrieval of
    demand instances for authenticated users, as well as handling
    cases when the demand does not exist or when the user is unauthenticated.
    """

    def setUp(self):
        """
        Set up a user, a KetoAppUser instance, and a Demand instance for testing.

        This method is called before each test method to ensure a clean state.
        It creates a test user, retrieves or creates the associated KetoAppUser,
        and initializes a Demand instance with predefined values.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.token = Token.objects.get(user=self.user)
        self.client = APIClient()

        self.keto_user = KetoAppUser.objects.get(user=self.user)
        self.demand = Demand.objects.create(
            keto_app_user=self.keto_user,
            kcal=2000,
            fat=70,
            protein=150,
            carbs=250
        )

    def test_retrieve_demand(self):
        """
        Test retrieving the demand instance for the authenticated user.
        Verifies that the response status is 200 OK and that the returned data matches
        the expected values for the demand instance's properties.
        """
        url = f"{reverse('demand-detail', kwargs={'pk': self.keto_user.id})}?token={self.token.key}"
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.demand.id)
        self.assertEqual(response.data['kcal'], self.demand.kcal)
        self.assertEqual(response.data['fat'], self.demand.fat)
        self.assertEqual(response.data['protein'], self.demand.protein)
        self.assertEqual(response.data['carbs'], self.demand.carbs)

    def test_retrieve_demand_not_found(self):
        """
        Test retrieving a demand instance that does not exist.
        This test verifies that an appropriate 404 NOT FOUND status is returned
        when retrieving a demand instance with a non-existent primary key.
        It ensures that the API correctly handles requests for demands that do not exist.
        """
        Demand.objects.all().delete()
        url = f"{reverse('demand-detail', kwargs={'pk': 999})}?token={self.token.key}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_demand_unauthenticated(self):
        """
        Test that an unauthenticated user cannot access the demand instance.
        This test checks that when a user is logged out, they are forbidden
        from accessing the demand instance. It verifies that the response
        status is 403 FORBIDDEN for requests made without authentication.
        """
        self.client.logout()
        url = f"{reverse('demand-detail', kwargs={'pk': self.keto_user.id})}"
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AllEventsAPIViewTest(APITestCase):
    def setUp(self):
        """Create a user and some FullDayIntake instances for testing."""
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.token = Token.objects.get(user=self.user)
        self.client = APIClient()

        self.event1 = FullDayIntake.objects.create(
            date='2025-01-01',
            total_kcal=2000,
            total_fat=70,
            total_protein=150,
            total_carbs=250,
            user=self.user.ketoappuser
        )

        self.event2 = FullDayIntake.objects.create(
            date='2025-01-02',
            total_kcal=1800,
            total_fat=60,
            total_protein=140,
            total_carbs=230,
            user=self.user.ketoappuser
        )

    def test_get_all_events(self):
        """Test retrieving all FullDayIntake instances for the logged-in user using token in URL."""

        url = f"{reverse('all-events')}?token={self.token.key}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = FullDayIntakeSerializer([self.event1, self.event2], many=True,
                                                context={'request': response.wsgi_request}).data
        self.assertEqual(response.data, expected_data)

    def test_get_no_events(self):
        """Test retrieving events when there are no FullDayIntake instances for the user."""

        new_user = User.objects.create_user(username='newuser', password='newpass')
        new_token = Token.objects.create(user=new_user)

        url = f"{reverse('all-events')}?token={new_token.key}"
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_events_unauthenticated(self):
        """Test retrieving events without authentication."""
        url = f"{reverse('all-events')}"
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)