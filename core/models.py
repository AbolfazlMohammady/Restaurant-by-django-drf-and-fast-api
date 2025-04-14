import re
from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxLengthValidator, MinLengthValidator




def validation_phone(value):
    if not value:  
        return 
    if not re.match(r'^09\d{9}$', value):
        raise ValidationError('شماره تلفن باید با 09 شروع شود و شامل 11 رقم باشد.')


class CustomUserManager(BaseUserManager):
    def create_user(self , phone=None, email=None, password=None, **extra_fields):
        if not phone and not email:
            raise ValueError('حداقل یکی از فیلدهای شماره تلفن یا ایمیل باید تنظیم شود.')

        user = self.model(phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self , phone=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('سوپرکاربر باید is_staff=True داشته باشد.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('سوپرکاربر باید is_superuser=True داشته باشد.')
        
        return self.create_user(phone, email, password, **extra_fields)
        

class User(AbstractUser):
    first_name = None
    last_name = None
    username = None

    ROLE_COURIER = 'CO'
    ROLE_RESTAURANT_OWNER = 'RO' 
    ROLE_CUSTOMER = 'CU'
    
    ROLE_USER_CHOICES = [
        (ROLE_COURIER, 'پیک'),
        (ROLE_RESTAURANT_OWNER,'رستوران دار'),
        (ROLE_CUSTOMER, 'مشتری'),
    ]

    phone = models.CharField(
        max_length=11, 
        null=True,
        blank=True, 
        validators=[
            MinLengthValidator(11),
            MaxLengthValidator(11),
            validation_phone 
        ],
        error_messages={'max_length': 'شماره تلفن باید 11 رقم باشد', 'min_length': 'شماره تلفن باید 11 رقم باشد'},
        unique=True
    )
    fullname = models.CharField(max_length=255, blank=True,null=True)
    image = models.ImageField(upload_to='core/profile/',blank=True , null=True)
    email = models.EmailField(blank=True, null=True )
    address = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=[('male','مرد'), ('female','زن')],blank=True, null=True)
    role = models.CharField(choices=ROLE_USER_CHOICES, max_length=2, default=ROLE_CUSTOMER)

    objects= CustomUserManager()
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]
    

    def __str__(self):
        return self.phone or self.email
    
    
    def save(self,*args, **kwargs):
        if self.pk:
            old_instance = self.__class__.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.image and self.image != old_instance.image:
                if default_storage.exists(old_instance.image.path):
                    default_storage.delete(old_instance.image.path)

        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.image and default_storage.exists(self.image.path):
            default_storage.delete(self.image.path)

        super().delete(*args, **kwargs)        