"""
This module contains tasks and functions that handle the automatic regeneration of
user authentication tokens in a Django application using Celery and Django Celery Beat.
The token regeneration task is designed to be executed periodically (every 30 days)
to ensure that user tokens are updated regularly for security purposes.

The main functionalities include:
- Regenerating expired tokens for users.
- Scheduling the token regeneration task with Celery Beat.
"""
from celery import shared_task
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.authtoken.models import Token


@shared_task
def regenerate_tokens():
    """
    This task identifies tokens that have been created more than 30 days ago,
    deletes them, and generates new tokens for the corresponding users.
    This task is designed to be run periodically using Celery Beat.
    """
    expiry_date = now() - timedelta(days=30)
    tokens = Token.objects.filter(created__lt=expiry_date)
    users = tokens.values_list("user_id", flat=True)

    to_create = [Token(user_id=user) for user in users]
    tokens.delete()
    Token.objects.bulk_create(to_create)
