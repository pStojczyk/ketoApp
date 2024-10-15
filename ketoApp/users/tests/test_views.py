"""
Tests for user API.
"""
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from calculator.models import FullDayIntake, Product
from .models import KetoAppUser, Demand
import datetime


class RegisterViewTest(TestCase):
    """Test register view"""

    def setUp(self):
        """Test client configuration"""
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_view_get(self):
        """Test registration form display (GET request)"""
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIn('form', response.context)

    def test_post_register_view_valid_form(self):
        """Test correct registration (POST request)"""
        payload = {
            'username': 'testuser',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
        }

        response = self.client.post(self.register_url, payload)

        self.assertRedirects(response, reverse('login'))

        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)

        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        self.assertEqual(len(all_messages), 1)
        self.assertEqual(all_messages[0].message, 'You have been successfully signed up testuser !')

    def test_post_register_view_invalid_form(self):
        """Test incorrect registration (POST request)"""
        payload = {
            'username': 'testuser',
            'password1': 'testpass123!',
            'password2': 'Differenttestpass1234!',
        }

        response = self.client.post(self.register_url, payload)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIn('form', response.context)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class ProfileViewTest(TestCase):
    """Test profile view"""

    def setUp(self):
        """Creating test user and login. Creating configuration for test user"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

        self.today = datetime.date.today()

        self.product1 = Product.objects.create(name='Product1', date=self.today, user=self.user)
        self.product2 = Product.objects.create(name='Product2', date=self.today, user=self.user)

        self.fulldayintake = FullDayIntake.objects.create(self.today, self.user, [self.product1, self.product2])

    def test_profile_view_renders_correct_template(self):
        """Test profile uses correct template"""
        response = self.client.get(reverse('profile'))

        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_context_data(self):
        """Test context view with correct data"""
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.context['today'], self.today)

        self.assertEqual(response.context['fulldayintake'], self.fulldayintake)

        self.assertIn(self.product1, response.context['products_list'])
        self.assertIn(self.product2, response.context['products_list'])

    def test_profile_view_without_fulldayintake(self):
        """Test missing fulldayintake in context view"""
        FullDayIntake.object.filter(date=self.today).delete()

        response = self.client.get(reverse('profile'))

        self.assertNotIn('fulldayintake', response.context)

    def test_profile_view_without_products(self):
        """Test missing products in context view"""
        Product.object.filter(date=self.today).delete()

        response = self.client.get(reverse('profile'))

        self.assertEqual(len(response.context['product_list']), 0)

    # def test_profile_redirects_if_not_logged_in(self):
    #     """Test correct redirection when user not logged in"""
    #     self.client.logout()
    #     response = self.client.get(reverse('profile'))
    #     self.assertRedirects(response, reverse('login'))


class KetoAppUserUpdateViewTest(TestCase):

    def setUp(self):
        """Creating configuration for test user"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.keto_app_user = KetoAppUser.objects.create(
            user=self.user,
            weight=70,
            height=180,
            age=40,
            gender=KetoAppUser.ActivityChoices.FEMALE,
            activity=KetoAppUser.ActivityChoices.MEDIUM,
        )

        self.update_url = reverse('keto_app_user_update', kwargs={'pk': self.keto_app_user.pk})

    def test_update_view_if_correct_URL(self):
        """Test view accessibility under specified URL and template"""
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/keto_app_user_form.html')

    def test_update_keto_app_user_with_correct_data(self):
        """Test correct update of keto_app_user"""
        updated_data = {
            'user': self.user,
            'weight': 70,
            'height': 180,
            'age': 40,
            'gender': KetoAppUser.ActivityChoices.FEMALE,
            'activity': KetoAppUser.ActivityChoices.MEDIUM,
        }

        response = self.client.post(self.update_url, updated_data)

        self.assertRedirects(response, reverse('profile'))

        self.keto_app_user.refresh_from_db()

        self.assertEqual(self.keto_app_user.weight, 70)
        self.assertEqual(self.keto_app_user.height, 180)
        self.assertEqual(self.keto_app_user.age, 40)
        self.assertEqual(self.keto_app_user.gender, KetoAppUser.ActivityChoices.FEMALE)
        self.assertEqual(self.keto_app_user.activity, KetoAppUser.ActivityChoices.MEDIUM)

    def test_update_keto_app_user_with_invalid_data(self):
        """Test incorrect update of keto_app_user"""
        invalid_data = {
            'weight': -70,
            'height': 180,
            'age': 40,
            'gender': KetoAppUser.ActivityChoices.FEMALE,
            'activity': KetoAppUser.ActivityChoices.MEDIUM,
        }

        response = self.client.post(self.update_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'weight', 'Value must be grater than or equal to 0.')

    def test_update_keto_app_user_with_None(self):
        """Test incorrect update of keto_app_user"""
        invalid_data = {
            'weight': None,
            'height': 180,
            'age': 40,
            'gender': KetoAppUser.ActivityChoices.FEMALE,
            'activity': KetoAppUser.ActivityChoices.MEDIUM,
        }

        response = self.client.post(self.update_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'weight', 'Please fill out this field.')

    # def test_update_keto_app_user_redirects_if_not_logged_in(self):
    #     """Test correct redirection when user not logged in"""
    #     self.client.logout()
    #     response = self.client.post(self.update_url)
    #     self.assertRedirects(response, reverse('login'))


class DemandDetailView(TestCase):
    def setUp(self):
        """Creating configuration for test user"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.keto_app_user = KetoAppUser.objects.create(
            user=self.user,
            weight=80,
            height=185,
            age=30,
            gender=KetoAppUser.ActivityChoices.MALE,
            activity=KetoAppUser.ActivityChoices.MEDIUM,
        )

        self.demand = Demand.object.create(
            user=self.user,
            kcal=2900,
            fat=127,
            protein=108,
            carbs=36
        )

        self.detail_url = reverse('keto_app_user_demand_detail', kwargs={'pk': self.demand.pk})

    def test_view_renders_correct_template(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/daily-requirements.html')

    def test_view_if_requires_login(self):
        """Test view if login required"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 302)
        # self.assertEqual(response.status_code, 404)
        self.assertRedirects(response, reverse('login'))

    def test_view_context_contains_demand(self):
        """Test view context with correct data"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('demand', response.context)
        self.assertEqual(response['demand'], self.demand)

    def test_access_demand_with_wrong_user(self):
        """Test access to demand with foreign user"""
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.other_keto_app_user = KetoAppUser.objects.create(
            user=self.other_user,
            weight=90,
            height=175,
            age=35,
            gender=KetoAppUser.GenderChoices.MALE,
            activity=KetoAppUser.ActivityChoices.LOW,
        )

        self.other_demand = Demand.objects.create(
            keto_app_user=self.other_keto_app_user,
            kcal=2555,
            fat=227,
            protein=95,
            carbs=31,
        )

        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('keto_app_user_demand_detail', kwargs={'pk': self.other_demand.pk}))
        self.assertEqual(response.status_code, 404)