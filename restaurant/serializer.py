from rest_framework import serializers
from django.shortcuts import get_object_or_404

from core.models import User
from .models import GenericImage, Restaurant , Menu


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
            model = GenericImage
            fields = ['id', 'image']

    def get_image(self, obj):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url


class UserRestaurntSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= ['id','fullname','phone']


class _Restaurant(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    owner= UserRestaurntSerializer(read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Restaurant
        fields= [
            'id',
            'name',
            'description',
            'address',
            'phone',
            'table',
            'desk_chair',
            'start_of_working_hours',
            'end_of_working_hours',
            'is_open',
            'created_at',
            'updated_at',
            'status',
            'owner',
            'images',
            ]


class RestaurantListSerializer(_Restaurant):
    menu_count = serializers.IntegerField(read_only=True)

    class Meta(_Restaurant.Meta):
        fields= [field for field in _Restaurant.Meta.fields if field not in {
            'status',
            'created_at',
            'updated_at',
            'description',
            'owner',
            'table',
            'desk_chair',
            'start_of_working_hours',
            'end_of_working_hours',
            }] + ['menu_count']
        

class MenuSeializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model= Menu
        fields = ['id','title','description','price','images']



class RestaurantDetailSerializer(_Restaurant):
    menu_items = MenuSeializer(many=True, read_only=True)

    class Meta(_Restaurant.Meta):
        fields = [
            field for field in _Restaurant.Meta.fields 
            if field not in {'created_at','updated_at','status'}
        ] + ['menu_items']

class RestaurantCreateSerializer(_Restaurant):
    images = serializers.ListField(
        child= serializers.ImageField(), write_only=True, required=False
    )

    class Meta(_Restaurant.Meta):
        fields= [field for field in _Restaurant.Meta.fields if field not in {'created_at','updated_at','status'}]

    def create(self, validated_data):
        images_data= validated_data.pop('images',[])
        user =get_object_or_404(User,pk=self.context['request'].user.id) 

        if  user.role != 'RO':
            
            validated_data['owner'] = user
            user.role = 'RO'
            user.save()
            restaurant= super().create(validated_data)

            for image_data in images_data:
                GenericImage.objects.create(
                    content_object=restaurant,
                    **image_data
                )
            return restaurant
        
        else:
            raise serializers.ValidationError({'detail':'شما قبلا یک رستوران ثبت کرده اید'})


class RestaurantUpdateSerializer(_Restaurant):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    deleted_images = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta(_Restaurant.Meta):
        fields = _Restaurant.Meta.fields + ['images', 'deleted_images']

    def validate(self, data):
        user = self.context['request'].user 
        owner = self.instance.owner

        if user != owner:
            raise serializers.ValidationError({'detail': 'فقط صاحب رستوران میتواند تغییرات را اعمال کند'})
        return data

    def update(self, instance, validated_data):
        image_data = validated_data.pop('images', [])
        deleted_image_ids = validated_data.pop('deleted_images', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for image_file in image_data:
            GenericImage.objects.create(content_object=instance, image=image_file)

        if deleted_image_ids:
            instance.images.filter(id__in=deleted_image_ids).delete()

        return instance


class MenuListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model= Menu
        fields=['id','title','price','is_available','images']

    
class MenuDetailSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    owner = UserRestaurntSerializer(read_only=True)


    class Meta:
        model= Menu
        fields=['title','description','price','is_available','owner','images']
