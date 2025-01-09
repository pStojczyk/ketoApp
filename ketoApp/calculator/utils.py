"""
Utility functions and classes for report generation, API connections, and email handling.
"""

import io
import requests

from django.conf import settings
from django.core.mail import EmailMessage

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class GetConnection:
    """
    A class to handle connection and data retrieval for a specific product's macronutrient information
    using an external food database API.
    """

    def __init__(self, product, grams):
        """
        Initializes the GetConnection instance with product name and weight.

        Args:
            product (str): The name of the product to retrieve data for.
            grams (int): The quantity of the product in grams.
        """

        self.product = product
        self.grams = grams

    def get_connection(self):
        """
        Sends a GET request to the food API to retrieve macronutrient information for the specified product and quantity.
        URL with necessary query parameters including the product name, grams, API ID, and API key.

        Returns:
            dict: JSON response containing the macronutrient information for the specified product.
        """

        params = f"?app_id={settings.FOOD_API_ID}&app_key=%20{settings.FOOD_API_KEY}&ingr={self.product}%20{self.grams}%20grams"
        result = requests.get(settings.FOOD_API_URL + params)
        return result.json()


class PDFReportGenerator:
    """ A class responsible for generating a PDF report with product details and summary information
    in a specified date range.
    """

    def __init__(self, products, summaries, start_date, end_date):
        """
        Initializes the PDFReportGenerator with products, summaries, and the date range.

        Args:
            products (QuerySet): The product records to be included in the report.
            summaries (QuerySet): The summary records of total macronutrients for each date.
            start_date (date): The start date of the report's date range.
            end_date (date): The end date of the report's date range.
        """

        self.products = products
        self.summaries = summaries
        self.start_date = start_date
        self.end_date = end_date
        self.buffer = io.BytesIO()

    def generate_report(self):
        """
        The method generates a PDF with a title indicating the date range of the report,
        followed by product details (name, date, kcal, fat, carbs, protein) and
        summary information (total kcal, fat, carbs, protein) for each date within
        the specified range.

        Returns:
            BytesIO: A buffer containing the generated PDF data, ready for email attachment.
        """

        c = canvas.Canvas(self.buffer, pagesize=A4)
        c.drawString(100, 800, f"Report for dates between {self.start_date} and {self.end_date}.")

        y_position = 750
        for product in self.products:
            for summary in self.summaries:
                if summary.date == product.date:
                    c.drawString(100, y_position, f"Product: {product.name}, "
                                                  f"date: {product.date}, "
                                                  f"kcal: {product.kcal}, "
                                                  f"fat: {product.fat}, "
                                                  f"carbs: {product.carb}, "
                                                  f"protein: {product.protein}"
                                 )

                    y_position -= 20

                c.drawString(100, y_position, f'Total kcal: {summary.total_kcal},'
                                              f'Date: {summary.date}, '
                                              f'Total fat: {summary.total_fat}, '
                                              f'Total carbs: {summary.total_carbs}, '
                                              f'Total protein: {summary.total_protein},'

                             )

                y_position -= 20

        c.showPage()
        c.save()
        self.buffer.seek(0)
        return self.buffer


class EmailSender:
    """
    This class is responsible for the construction and sending of an email message
    that includes a PDF report as an attachment.
    """

    def __init__(self, email, subject, body, pdf_buffer, start_date, end_date):
        """
        Initialize the email message with content and attachment data.

        Args:
            email (str): Recipient's email address.
            subject (str): Subject line for the email.
            body (str): Body text of the email.
            pdf_buffer (BytesIO): Buffer containing the PDF attachment data.
            start_date (date): Start date for report, used in attachment filename.
            end_date (date): End date for report, used in attachment filename.
        """

        self.email = email
        self.subject = subject
        self.body = body
        self.pdf_buffer = pdf_buffer
        self.start_date = start_date
        self.end_date = end_date

    def send_email(self):
        """
        Constructs an `EmailMessage` object with the specified subject,
        body and receiver. Attaches the PDF report, named with the report
        date range, and sends the message using Django's email backend.
        """

        email_message = EmailMessage(
            subject=self.subject,
            body=self.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.email],
        )
        email_message.attach(f"report_{self.start_date}_{self.end_date}.pdf",
                             self.pdf_buffer.getvalue(),
                             'application/pdf',
                             )
        email_message.send()
