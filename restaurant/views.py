from django.db.models import Count, Q
from django.db.models import Prefetch
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions

from .permission import IsOwnerObject
from .pagination import get_pagination
from .models import GenericImage, Restaurant, Menu
from .serializer import (
    RestaurantListSerializer, 
    RestaurantCreateSerializer,
    RestaurantDetailSerializer,
    RestaurantUpdateSerializer,
    # Menu
    MenuListSerializer,
    MenuDetailSerializer
    ) 

class RestaurntViewSet(viewsets.ViewSet):

    def get_permissions(self):

        action = getattr(self, 'action', None)

        if self.action in ['delete_restaurant','update_restaurant']:
            return [IsOwnerObject(),permissions.IsAuthenticated()]
        if self.action in ['create_restaurant']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
    

    def filter_menu(self, queryset, request):

        filter_by_name = request.query_params.get('name')
        if filter_by_name:
            queryset = queryset.filter(title__icontains=filter_by_name)    

        filter_by_price = request.query_params.get('price')
        if filter_by_price:
            queryset=queryset.filter(price__lte=filter_by_price)

        return queryset

    def filter_restaurnt(self, queyset, request):
        """اعمال فیلترها برای لیست رستوران ها"""

        filter_by_name = request.query_params.get('name')
        if filter_by_name:
            queyset = queyset.filter(name__icontains=filter_by_name)
        
        filter_by_address = request.query_params.get('province')
        if filter_by_address:
            queyset= queyset.filter(address__icontains=filter_by_address)

        return queyset

    def list_restaurant(self, request):

        queryset = Restaurant.objects.\
            select_related('owner').\
            annotate(menu_count=Count("menu_items")).\
            prefetch_related(Prefetch('images', queryset=GenericImage.objects.all())).\
            filter(status='C' , is_open=True)
        
        queryset = self.filter_restaurnt(queryset,request)
        paginator , restaurant_paginator = get_pagination(queryset, request)

        serializer = RestaurantListSerializer(restaurant_paginator, many=True)
        return paginator.get_paginated_response(serializer.data)

    
    def detail_restaurant(self, request, pk: int):
        try:
           queryset = Restaurant.objects.\
                select_related('owner').\
                prefetch_related(
                    Prefetch('images', queryset=GenericImage.objects.all()),
                    Prefetch('menu_items', queryset=Menu.objects.filter(is_available=True).prefetch_related('images'))
                ).get(id=pk)
        except Restaurant.DoesNotExist:
            return Response({'detail':'Restarnt not Found!!!'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RestaurantDetailSerializer(queryset,  context={'request': request})
        return Response(serializer.data , status=status.HTTP_200_OK)
    

    def create_restaurant(self, request):
        serializer = RestaurantCreateSerializer(data= request.data, context={'request':request})

        if serializer.is_valid():
            restaurant = serializer.save()
            return Response(RestaurantDetailSerializer(restaurant).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def update_restaurant(self, request, pk):
        try:
            queryset = Restaurant.objects.select_related('owner').prefetch_related(
                Prefetch('images', queryset=GenericImage.objects.all()),
                Prefetch('menu_items', queryset=Menu.objects.prefetch_related('images').all())
            ).get(id=pk)
        except Restaurant.DoesNotExist:
            return Response({'detail': 'Restaurant not Found!!!'}, status=status.HTTP_404_NOT_FOUND)
        
        self.check_object_permissions(request, queryset)
        serializer = RestaurantUpdateSerializer(queryset, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            restaurant = serializer.save()
            return Response(RestaurantDetailSerializer(restaurant).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete_restaurant(self, request,pk):
        try:
            queryset = Restaurant.objects.select_related('owner').prefetch_related(
                Prefetch('images', queryset=GenericImage.objects.all()),
                Prefetch('menu_items', queryset=Menu.objects.prefetch_related('images').all())
            ).get(id=pk)
        except Restaurant.DoesNotExist:
            return Response({'detail': 'Restaurant not Found!!!'}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request,queryset)
        user=request.user
        queryset.delete()
        user.role = 'CU'
        user.save()
        return Response({'detail': f'{queryset.name} succsses deleted!!'}, status=status.HTTP_204_NO_CONTENT)
        
    

    def list_menu(self,request,restaurant_id):
        try:
            queryset = Menu.objects.filter(restaurant_id=restaurant_id, is_available=True)
        except Restaurant.DoesNotExist:
            return Response({'erorr':"همچین رستورانی نیست"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.filter_menu(queryset, request)
        paginator , menu_paginator = get_pagination(queryset, request)
        
        serializer = MenuListSerializer(menu_paginator, many=True)
        return paginator.get_paginated_response(serializer.data)
    

    def detail_menu(self, request,restaurant_id, menu_id):
        try:
            queryset= Menu.objects.select_related('owner').get(id=menu_id)
        except Menu.DoesNotExist:
            return Response({'erorr':"همچین منوی وجود ندارد"}, status=status.HTTP_400_BAD_REQUEST)

        serilizer= MenuDetailSerializer(queryset)
        return Response(serilizer.data, status=status.HTTP_200_OK)



