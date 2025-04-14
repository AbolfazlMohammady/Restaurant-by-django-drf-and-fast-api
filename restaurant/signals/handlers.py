from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from restaurant.models import GenericImage

@receiver(post_delete, sender=GenericImage)
def delete_image_file(sender, instance, **kwargs):
    if instance.image and default_storage.exists(instance.image.path):
        default_storage.delete(instance.image.path)
