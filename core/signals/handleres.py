from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from core.models import User

@receiver(post_delete, sender=User)
def delete_image_profile(sender, instance, **kwargs):
    if instance.image and default_storage.exists(instance.image.path):
        default_storage.delete(instance.image.path)