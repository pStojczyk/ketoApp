"""
Tests for user API.
"""
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse


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

