from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import KetoAppUser


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        KetoAppUser.objects.create(user=instance)


@receiver(post_save, sender=KetoAppUser)
def create_or_update_demand(sender, instance, created, **kwargs):
    if not created:
       instance.update_or_create_demand()


