"""
Tests for calculator API.
"""

import datetime
from datetime import date
import json
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User

from calculator.forms import ProductRequestForm
from calculator.models import FullDayIntake, Product


class ProductMacroNutrientsCreateTests(TestCase):
    """Test which allows users to create Product instances with specified macronutrient data."""

    def setUp(self):
        """
        Set up test data, including a logged-in user instance for authentication,
        and sample data for testing both valid and invalid POST requests.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.url = reverse('product_create', args=[str(date.today())])

        self.valid_data = {
            "product_name": "Apple",
            "grams": 100
        }
        self.invalid_data = {
            "product_name": "1Apple",
            "grams": -50,
        }

    @patch("calculator.utils.GetConnection.get_connection")
    def test_post_valid_data_creates_product(self, mock_get_connection):
        """
        Test where a POST request with valid data successfully creates a new Product instance.
        - Mocks the GetConnection API to return macronutrient data.
        - Checks that a Product instance is created with the expected values.
        - Confirms a redirect to the profile page after successful form submission.
        """

        mock_get_connection.return_value = {
            "calories": 52,
            "totalNutrients": {
                "CHOCDF": {"quantity": 14},
                "FAT": {"quantity": 0.2},
                "PROCNT": {"quantity": 0.3},
            },
        }

        response = self.client.post(self.url, data=self.valid_data)

        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(product.name, "Apple")
        self.assertEqual(product.grams, 100)
        self.assertEqual(product.kcal, 52)
        self.assertEqual(product.carb, 14)
        self.assertEqual(product.fat, 0)
        self.assertEqual(product.protein, 0)
        self.assertEqual(product.date, date.today())

        self.assertRedirects(response, reverse("profile"))

    def test_post_invalid_data_returns_form_with_errors(self):
        """
        Test if POST request with invalid data renders the form with errors.
        - Submits invalid form data.
        - Ensures no Product instance is created.
        - Confirms that the form is returned with validation errors.
        """

        response = self.client.post(self.url, data=self.invalid_data)

        self.assertEqual(Product.objects.count(), 0)

        form = response.context["form"]
        self.assertIsInstance(form, ProductRequestForm)
        self.assertFalse(form.is_valid())
        self.assertIn('product_name', form.errors)
        self.assertIn("Product name can not contain digits", form.errors['product_name'][0])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calculator/product_nutrients_form.html")

    def test_get_request_renders_form(self):
        """
       Ensure that the GET request correctly renders the form template and passes
        an empty form and selected date to the template.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calculator/product_nutrients_form.html")
        self.assertIsInstance(response.context['form'], ProductRequestForm)
        self.assertEqual(response.context['selected_date'], str(date.today()))

    def test_unauthenticated_user_redirect(self):
        """
        Test if unauthenticated user is redirected to the login page.
        - logs out the current user.
        - attempts to access the view and verifies that the user is redirected to login.
        """

        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class ProductMacroNutrientsUpdateTests(TestCase):
    """
    Test cases for the ProductMacroNutrientsUpdate view.
    These tests verify the behavior of updating an existing Product, correct redirections,
    form handling, and database updates for both valid and invalid data.
    """

    def setUp(self):
        """
        Sets up a logged-in user and creates a Product instance for testing.
        The test user and product instance are used in the update view tests to check
        if the view correctly updates or rejects changes to the product.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.product = Product.objects.create(
            name="Apple",
            grams=100,
            kcal=52,
            carb=14,
            fat=0.2,
            protein=0.3,
            date=datetime.date.today()
        )

        self.product.user.set([self.user.ketoappuser])

        self.url = reverse("product_update", kwargs={"pk": self.product.id})
        self.valid_data = {"grams": 150}
        self.invalid_data = {"grams": -50}

    @patch("calculator.views.GetConnection.get_connection")
    @patch("calculator.views.ProductRequestForm")
    def test_post_valid_data_updates_product(self, mock_form, mock_get_connection):
        """
        Tests if POST request with valid data updates the product in the database.
        Verifies that the macronutrient values are recalculated based on the new weight (grams)
        and the user is redirected appropriately if the product date is today.
        """
        form = MagicMock()
        form.is_valid.return_value = True
        form.cleaned_data = dict(grams=100)
        mock_form.return_value = form

        mock_get_connection.return_value = {
            "calories": 78,
            "totalNutrients": {
                "CHOCDF": {"quantity": 21},
                "FAT": {"quantity": 0.3},
                "PROCNT": {"quantity": 0.4},
            },
        }

        response = self.client.post(self.url, data=self.valid_data)

        self.product.refresh_from_db()

        self.assertEqual(self.product.grams, 100)
        self.assertEqual(self.product.kcal, 78)
        self.assertEqual(self.product.carb, 21)
        self.assertEqual(self.product.fat, 0)
        self.assertEqual(self.product.protein, 0)

        self.assertRedirects(response, reverse("profile"))

    def test_post_invalid_data_returns_form_with_errors(self):
        """
        Tests if POST request with invalid data returns the form with errors.
        Verifies that the form is displayed with errors and no changes are made to the product.
        """

        response = self.client.post(self.url, data=self.invalid_data)

        self.product.refresh_from_db()

        self.assertEqual(self.product.grams, 100)
        form = response.context["form"]
        self.assertIsInstance(form, ProductRequestForm)
        self.assertTrue(form.errors)
        self.assertFalse(form.is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calculator/product_nutrients_form.html")

    def test_get_request_renders_form_with_prefilled_data(self):
        """
        Tests if GET request renders the update form pre-filled with product data.
        Verifies that the product name field is hidden.
        """

        response = self.client.get(self.url)

        form = response.context["form"]
        self.assertIsInstance(form, ProductRequestForm)
        self.assertEqual(form.initial["product_name"], "Apple")
        self.assertTrue(form.fields["product_name"].widget.is_hidden)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calculator/product_nutrients_form.html")

    @patch("calculator.utils.GetConnection.get_connection")
    @patch("calculator.views.ProductRequestForm")
    def test_redirect_to_products_list_by_date_for_non_today_product(self, mock_form, mock_get_connection):
        """
        Tests which updates product with a date other than today redirects to the products_list_by_date.
        Changes the date of the product to simulate updating an older product and checks redirection.
        """
        form = MagicMock()
        form.is_valid.return_value = True
        form.cleaned_data = dict(grams=100)
        mock_form.return_value = form

        self.product.date = datetime.date(2025, 1, 1)
        self.product.save()

        mock_get_connection.return_value = {
            "calories": 78,
            "totalNutrients": {
                "CHOCDF": {"quantity": 21},
                "FAT": {"quantity": 0.3},
                "PROCNT": {"quantity": 0.4},
            },
        }

        response = self.client.post(self.url, data=self.valid_data)

        self.assertRedirects(response, reverse("products_list_by_date", args=[self.product.date]))

    def test_unauthenticated_user_redirect(self):
        """
        Tests that an unauthenticated user attempting to access the view is redirected to log in.
        Logs out the user and attempts to access the update view to confirm redirection.
        """

        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class ProductDetailViewTests(TestCase):
    """
    Tests for the ProductDetailView
    - Correct rendering of the product details page,
    - Handling of the case when the product does not exist,
    - Redirection for unauthenticated users.
    """

    def setUp(self):
        """
        Creates a logged-in user and a product to be tested.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.product = Product.objects.create(
            name="Apple",
            grams=100,
            kcal=52,
            carb=14,
            fat=0.2,
            protein=0.3,
        )

        self.product.user.set([self.user.ketoappuser])

        self.url = reverse('product_detail', kwargs={'pk': self.product.pk})

    def test_product_detail_view(self):
        """
        Tests that the ProductDetailView correctly renders the product details page.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'calculator/single_product_nutrients.html')

        self.assertIn('product', response.context)

        product = response.context['product']
        self.assertEqual(product.name, "Apple")
        self.assertEqual(product.grams, 100)
        self.assertEqual(product.kcal, 52)
        self.assertEqual(product.carb, 14)
        self.assertEqual(product.fat, 0)
        self.assertEqual(product.protein, 0)

    def test_product_not_found(self):
        """
        Tests that the view returns a 404 status code when the product does not exist.
        """
        invalid_url = reverse('product_detail', kwargs={'pk': 9999})

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_redirect(self):
        """
        Tests that an unauthenticated user is redirected to the login page.
        """
        self.client.login(username="testuser", password="testpassword")

        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class ProductListByDateViewTests(TestCase):
    """
    Tests for the ProductListByDateView to ensure that the view properly:
    - renders the list of products for a specific date.
    - includes FullDayIntake data when available.
    - redirect for unauthenticated users.
    """

    def setUp(self):
        """
        Creates a logged-in user and a product to be tested.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.date_str = str(date.today())

        self.product = Product.objects.create(
            name="Apple",
            grams=100,
            kcal=52,
            carb=14,
            fat=0.2,
            protein=0.3,
            date=self.date_str,
        )

        self.product.user.set([self.user.ketoappuser])
        self.product.save()

        self.url = reverse('products_list_by_date', kwargs={'date': self.date_str})

    def test_fulldayintake_is_created_by_signal(self):
        """"Test if fulldayintake is created"""

        self.assertEqual(FullDayIntake.objects.filter(user=self.user.ketoappuser).count(), 1)

    def test_product_list_view(self):
        """
        Tests that the ProductListByDateView renders the correct template
        and includes the appropriate context for the given date.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'calculator/list_products.html')

        self.assertIn('date', response.context)
        self.assertEqual(response.context['date'], self.date_str)

        self.assertIn('product_by_date', response.context)
        self.assertEqual(response.context['product_by_date'].count(), 1)
        self.assertEqual(response.context['product_by_date'][0].name, "Apple")

        self.assertIn('fulldayintake', response.context)
        self.assertEqual(response.context['fulldayintake'].total_kcal, 52)

    def test_unauthenticated_user_redirect(self):
        """
        Tests that an unauthenticated user is redirected to the login page when.
        """

        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class ProductDeleteViewTests(TestCase):
    """
    Test for the ProductDeleteView to ensure that the view allows logged-in users to delete a product.
    - allows correct redirection after deletion based on the product's date.
    - properly handles unauthenticated users.
    """

    def setUp(self):
        """
        Creates a logged-in user and a product to be deleted.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.product = Product.objects.create(
            name="Apple",
            grams=100,
            kcal=52,
            carb=14,
            fat=0.2,
            protein=0.3,
            date=str(date.today())
        )

        self.product.user.set([self.user.ketoappuser])

        self.url = reverse('product_delete', kwargs={'pk': self.product.pk})

    def test_product_delete_view(self):
        """
        Tests that the ProductDeleteView allows a logged-in user to delete a product,
        and redirects to the correct URL after deletion based on the product's date.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'calculator/delete_product_confirm.html')

        response = self.client.post(self.url)

        self.assertEqual(Product.objects.count(), 0)

        self.assertRedirects(response, reverse_lazy('profile'))

    def test_product_delete_redirect_to_product_list(self):
        """
        Tests that if the product's date is not today, the user is redirected to the product list
        for the specified date after deletion.
        """

        future_date = date(2024, 11, 18)
        future_product = Product.objects.create(
            name="Banana",
            grams=120,
            kcal=100,
            carb=25,
            fat=0.3,
            protein=1.5,
            date=str(future_date)
        )

        future_product.user.set([self.user.ketoappuser])

        future_url = reverse('product_delete', kwargs={'pk': future_product.pk})

        response = self.client.post(future_url)

        self.assertEqual(Product.objects.count(), 1)

        self.assertRedirects(response, reverse('products_list_by_date', args=[str(future_date)]))

    def test_unauthenticated_user_redirect(self):
        """
        Tests that an unauthenticated user is redirected to the login page when attempting
        to access the ProductDeleteView.
        """

        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_product_delete_not_found(self):
        """
        Tests that a 404 error is returned when trying to delete a non-existent product.
        """

        invalid_url = reverse('product_delete', kwargs={'pk': 9999})

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, 404)


class SummaryViewTests(TestCase):
    """
    Tests for the SummaryView to ensure that the view correctly displays full day intake summary.
    - tests if correct template is used for rendering.
    - tests if Unauthenticated users are redirected to the login page.
    """

    def setUp(self):
        """
        Creates a logged-in user and a signal for FullDayIntake.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.fulldayintake = FullDayIntake.objects.create(
            date=datetime.date.today(),
            total_kcal=320,
            total_carbs=1,
            total_fat=14,
            total_protein=44,
            user=self.user.ketoappuser
        )

        self.url = reverse('summary', kwargs={'pk': self.fulldayintake.pk})

    def test_summary_view(self):
        """
        Test that the SummaryView correctly renders the daily intake details for the logged-in user.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'calculator/summary.html')

        self.assertIn('object', response.context)

        full_day_intake = response.context['object']
        self.assertEqual(full_day_intake.user, self.user.ketoappuser)
        self.assertEqual(full_day_intake.date, date.today())
        self.assertEqual(full_day_intake.total_kcal, 320)
        self.assertEqual(full_day_intake.total_carbs, 1)
        self.assertEqual(full_day_intake.total_fat, 14)
        self.assertEqual(full_day_intake.total_protein, 44)

    def test_unauthenticated_user_redirect(self):
        """
        Test if unauthenticated user is redirected to the login page when attempting to access the summary view.
        """

        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_summary_view_not_found(self):
        """
        Test that a 404 error is returned if the FullDayIntake object does not exist for the provided ID.
        """

        invalid_url = reverse('summary', kwargs={'pk': 9999})

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, 404)


class CalendarViewTests(TestCase):
    """
    Tests for the CalendarView to ensure that view correctly displays the calendar for logged-in users.
    - Unauthenticated users are redirected to the login page.
    - The correct data is passed to the template (list of FullDayIntake events).
    """

    def setUp(self):
        """
        Sets up the test environment, creates a logged-in user.
        Creates several FullDayIntake objects to test the calendar view.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.fulldayintake1 = FullDayIntake.objects.create(
            date=str(date.today()),
            total_kcal=2000,
            total_protein=150,
            total_fat=70,
            total_carbs=250,
            user=self.user.ketoappuser
        )

        self.fulldayintake2 = FullDayIntake.objects.create(
            date='2025-01-01',
            total_kcal=2000,
            total_protein=150,
            total_fat=70,
            total_carbs=250,
            user=self.user.ketoappuser
        )

        self.url = reverse('calendar')

    def test_calendar_view_authenticated(self):
        """
        Tests that an authenticated user can view the calendar with FullDayIntake events.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'calculator/calendar.html')

        self.assertIn('events', response.context)

        events = response.context['events']

        expected_events = [
            {
                'title': f'TOTAL KCAL: {self.fulldayintake1.total_kcal}',
                'start': self.fulldayintake1.date,
                'url': f'/list/{self.fulldayintake1.date}/',
                'details': f'TOTAL FAT: {self.fulldayintake1.total_fat},\nTOTAL PROTEIN: {self.fulldayintake1.total_protein},\nTOTAL CARBS: {self.fulldayintake1.total_carbs}'
            },
            {
                'title': f'TOTAL KCAL: {self.fulldayintake2.total_kcal}',
                'start': self.fulldayintake2.date,
                'url': f'/list/{self.fulldayintake2.date}/',
                'details': f'TOTAL FAT: {self.fulldayintake2.total_fat},\nTOTAL PROTEIN: {self.fulldayintake2.total_protein},\nTOTAL CARBS: {self.fulldayintake2.total_carbs}'
            }
        ]

        for expected_event in expected_events:
            self.assertIn(expected_event, events)

    def test_calendar_view_unauthenticated(self):
        """
        Tests that an unauthenticated user is redirected to the login page.
        """

        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_calendar_view_no_events(self):
        """
        Tests the behavior when no FullDayIntake entries are created.
        """
        
        FullDayIntake.objects.filter(user=self.user.ketoappuser).delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'calculator/calendar.html')

        self.assertIn('events', response.context)
        self.assertEqual(len(response.context['events']), 0)


class SendReportPdfViewTests(TestCase):
    """
    Tests for the SendReportPdfView to ensure the form displays correctly,
    triggers email sending only if products exist, and handles each case properly.
    """

    def setUp(self):
        """
        Sets up the test environment by creating a logged-in test user and sample products.
        """

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.product1 = Product.objects.create(
            name="Apple",
            grams=100,
            kcal=52,
            carb=14,
            fat=0.2,
            protein=0.3,
            date="2024-11-12"
        )

        self.product2 = Product.objects.create(
            name="Banana",
            grams=200,
            kcal=100,
            carb=90,
            fat=0.5,
            protein=0.2,
            date="2024-11-13"
        )

        self.product1.user.set([self.user.ketoappuser])
        self.product2.user.set([self.user.ketoappuser])

        self.url = reverse('send_report_pdf')

    @patch('calculator.views.send_report.delay')
    def test_send_report_with_existing_products(self, mock_send_report):
        """
        Tests that the view correctly processes the form, checks for products,
        and send report task if products exist in the specified date range.
        """

        form_data = {
            'start_date': "2024-11-12",
            'end_date': "2024-11-13",
            'email': "test@example.com",
        }
        response = self.client.post(self.url, data=form_data)

        self.assertTemplateUsed(response, "calculator/send_email_success.html")

        mock_send_report.assert_called_once_with(self.user.id, "test@example.com", datetime.date(2024, 11, 12), datetime.date(2024, 11, 13))

    def test_no_products_in_date_range(self):
        """
        Tests that the view renders a "no products found" template if there are no products
        in the specified date range, ensuring no email is sent.
        """
        form_data = {
            'start_date': "2024-01-01",
            'end_date': "2024-01-02",
            'email': "test@example.com",
        }

        response = self.client.post(self.url, data=form_data)

        self.assertTemplateUsed(response, "calculator/no_product_found.html")

    @patch('calculator.views.send_report.delay')
    def test_send_report_form_invalid(self, mock_send_report):
        """
        Tests that invalid form data (e.g., missing email) prevents the form from
        processing and does not trigger the email sending task.
        """
        form_data = {
            'start_date': "2024-11-12",
            'end_date': "2024-11-13",
            'email': "",
        }
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

        mock_send_report.assert_not_called()
