from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product


@receiver(post_save, sender=Product)
def post_save_product(sender, instance, created, **kwargs):
    """
    This function is connected to the `post_save` signal of the `Product` model.
    When a Product instance is created or updated, it calls the `update_or_create_fulldayintake`
    method on the `Product` instance to ensure the related FullDayIntake data is updated or created accordingly.

    Args:
        sender (Model): The model class that sent the signal is `Product`.
        instance (Product): The actual instance of the `Product` model that was saved.
        created (bool): A flag indicating whether the instance was created (True) or updated (False).
        **kwargs: Additional keyword arguments passed by the signal.
    """

    instance.update_or_create_fulldayintake()




