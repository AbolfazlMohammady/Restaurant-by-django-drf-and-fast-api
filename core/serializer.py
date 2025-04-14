from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields = ['phone', 'email','password']
        extra_kwargs = {"password": {"write_only": True}}


class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display', read_only= True)
    gender = serializers.CharField(source='get_gender_display')
    
    class Meta:
        model= User
        fields = ['phone', 'email','fullname', 'gender', 'address', 'image', 'role']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields = ['phone', 'email','fullname', 'gender', 'address', 'image', 'role']

