"""
Asynchronous tasks for report generation and email sending in KetoApp.
"""

import logging

from .models import Product, FullDayIntake
from .utils import EmailSender, PDFReportGenerator
from ketoApp.celery import app


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('my_logs.log'),
        logging.StreamHandler()
    ]

)


@app.task(name="calculator.tasks.send_report")
def send_report(user_id, email, start_date, end_date):
    """
        Generates a PDF report of dietary intake within a specified date range and sends email it to the user.

        This function:
            - Queries products and summary records within the specified date range.
            - Logs a message if no products are found for the specified dates.
            - Generates a PDF report with products and summarizing data.
            - Sends an email with the PDF report attached.
            - Logs the information of the report generation and email sending.

        Returns:
            None
        """
    logger.info("Start generating PDF report for user: %s to %s", user_id, email)

    products = Product.objects.filter(date__range=[start_date, end_date], user__user_id=user_id)
    summaries = FullDayIntake.objects.filter(date__range=[start_date, end_date], user__user_id=user_id)

    pdf_generator = PDFReportGenerator(products, summaries, start_date, end_date)
    pdf_buffer = pdf_generator.generate_report()

    email_subject = f"KetoApp report for dates between {start_date} and {end_date}."
    email_body = "Please find the report attached in PDF format."
    email_sender = EmailSender(email, email_subject, email_body, pdf_buffer, start_date, end_date)
    email_sender.send_email()

    logger.info("PDF report has been generated and sent for user: %s to %s", user_id, email)

