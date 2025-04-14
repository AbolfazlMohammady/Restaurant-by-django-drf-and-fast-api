from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch


from core.models import User
from restaurant.models import Menu, Restaurant, GenericImage
from restaurant.serializer import ImageSerializer


class MenuCreateSeializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Menu
        fields = ['title', 'description', 'price', 'is_available', 'restaurant', 'owner', 'images']
        read_only_fields = ['restaurant', 'owner']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        user = self.context['request'].user

        if user.role != 'RO':
            raise serializers.ValidationError(detail='برای ساخت منو شما باید یک رستوران ثبت کنید')

        restaurant = Restaurant.objects.filter(owner=user).first()
        if not restaurant:
            raise serializers.ValidationError(detail='شما هنوز رستورانی ثبت نکرده‌اید')

        validated_data['owner'] = user
        validated_data['restaurant'] = restaurant

        menu = super().create(validated_data)


        for image_file in images_data:
            GenericImage.objects.create(content_object=menu, image=image_file)

        return menu


class MenuUpdateSerializr(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Menu
        fields = ['title', 'description', 'price', 'is_available','restaurant', 'owner', 'images','deleted_images']
        read_only_fields = ['restaurant', 'owner']

    def validate(self, data):
        user= self.context['request'].user
        owner_restarant = self.instance.restaurant.owner
        if user != owner_restarant:
            raise serializers.ValidationError(detail='فقط صازنده رستوران حق تغییر منو را دارد')

        return data

    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('images',[])
        deleted_image_ids  = validated_data.pop('deleted_images',[])
        
        for att, value in validated_data.items():
            setattr(instance ,att, value)
        instance.save()

        for image_file in images_data:
            GenericImage.objects.create(content_object=instance, image=image_file)

        if deleted_image_ids:
            instance.images.filter(id__in=deleted_image_ids).delete()

        return instance