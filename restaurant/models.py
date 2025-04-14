from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator


def upload_to_generic(instance, filename):
    model_name = instance.content_type.model
    return f"uploads/{model_name}/{instance.object_id}/{filename}"


class GenericImage(models.Model):
    image = models.ImageField(upload_to=upload_to_generic)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.content_object}"  # e.g., Restaurant: X

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = GenericImage.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.image != self.image:
                if default_storage.exists(old_instance.image.path):
                    default_storage.delete(old_instance.image.path)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and default_storage.exists(self.image.path):
            default_storage.delete(self.image.path)
        super().delete(*args, **kwargs)


class Restaurant(models.Model):
    STATUS_COMPLETED = 'C'
    STATUS_UNDER_REVIEW = 'UR'
    STATUS_REJECTED = 'R'

    STATUS_CHOICES = [
        (STATUS_COMPLETED, 'تایید شده'),
        (STATUS_UNDER_REVIEW, 'درحال برسی'),
        (STATUS_REJECTED, 'ردشده')
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=512, blank=True, null=True)
    phone = models.CharField(max_length=23, help_text='شماره تلفن همراه/رستوران را وارد کنید')
    table = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    desk_chair = models.PositiveSmallIntegerField()
    start_of_working_hours = models.TimeField()
    end_of_working_hours = models.TimeField()
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_UNDER_REVIEW)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants')

    images = GenericRelation(GenericImage)

    def __str__(self):
        return self.name


class Menu(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.PositiveSmallIntegerField(help_text='قیمت را به تومان وارد کنید')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='menus', null=True)

    images = GenericRelation(GenericImage)

    def __str__(self):
        return self.title
