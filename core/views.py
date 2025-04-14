from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from rest_framework import views, status, viewsets , permissions

from .models import User
from .serializer import ProfileSerializer, ProfileUpdateSerializer


class ProfileViewSet(viewsets.ViewSet):
    permission_classes=[permissions.IsAuthenticated]

    def retreive(self, request):
        serializer= ProfileSerializer(request.user)
        return Response(serializer.data)

    def update(self, request):
        serializer = ProfileUpdateSerializer(request.user, data= request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {"detail": "هر دو فیلد 'رمز عبور قدیمی' و 'رمز عبور جدید' لازم هستند."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not check_password(old_password, user.password):
            return Response(
                {"detail": "رمز عبور قدیمی اشتباه است."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user.set_password(new_password)
        user.save()
        return Response({"detail": "رمز عبور با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def delete_account(self, request):
        user= request.user
        confirm = request.data.get('confirm')

        if confirm != 'yes':
            return Response({'detail': 'برای حذف اکانت باید تایید کنید'}, status=status.HTTP_400_BAD_REQUEST)


        if confirm == "yes":
            user.is_active = False
            user.save()
            
            # user.delete()  

            return Response({"detail": "حساب کاربری شما با موفقیت حذف شد."}, status=status.HTTP_200_OK)
        