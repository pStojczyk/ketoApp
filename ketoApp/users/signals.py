"""
Signal handlers for creating and updating user profiles and dietary demands.
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .models import KetoAppUser


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
        Signal handler that creates a `KetoAppUser` profile when a new `User` is created.

        Args:
            sender (Model): The User model that sends the signal.
            instance (User): The actual instance of the `User` that was saved.
            created (bool): Flag that indicates if a new `User` was created.
            **kwargs: Additional keyword arguments passed with the signal.
        """

    if created and not KetoAppUser.objects.filter(user=instance).exists():
        KetoAppUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=KetoAppUser)
def create_or_update_demand(sender, instance, created, **kwargs):
    """
    Signal handler that updates or creates the dietary demand for a `KetoAppUser`.

    Args:
        sender (Model): The KetoAppUser model that sends the signal.
        instance (KetoAppUser): The actual instance of the `KetoAppUser` that was saved.
        created (bool): Flag that indicates if a new `KetoAppUser` was created.
        **kwargs: Additional keyword arguments passed with the signal.
    """

    if not created:
        instance.update_or_create_demand()


