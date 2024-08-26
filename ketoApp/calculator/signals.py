from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product


@receiver(post_save, sender=Product)
def post_save_product(sender, instance, created, **kwargs):
    instance.update_or_create_fulldayintake()



