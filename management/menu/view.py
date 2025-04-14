from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from restaurant.models import Menu
from restaurant.serializer import MenuDetailSerializer, MenuListSerializer
from .serializer import MenuCreateSeializer

class MenuManegement(viewsets.ViewSet):

    def get_permissions(self):
        action = getattr(self, 'action', None)

        if self.action in ['list_menu','detail_menu']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    

    def list_menu(self, request):
        queryset= Menu.objects.select_related('owner','restaurant__owner').filter(owner=request.user)
        
        self.check_object_permissions(queryset, request)
        serializer= MenuListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def detail_menu(self,request, pk):
        try:
            queryset= Menu.objects.select_related('owner','restaurant__owner').get(id=pk)
        except Menu.DoesNotExist:
            return Response({'erorr':"همچین منوی وجود ندارد"}, status=status.HTTP_400_BAD_REQUEST)
        
        self.check_object_permissions(queryset, request)

        serilizer= MenuDetailSerializer(queryset)
        return Response(serilizer.data, status=status.HTTP_200_OK)
        
    
    def create_menu(self,request):
        serializer = MenuCreateSeializer(data=request.data, context= {'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def  update_menu(self, request, pk):
        try:
            queryset= Menu.objects.select_related('owner','restaurant__owner').get(id=pk)
        except Menu.DoesNotExist:
            return Response({'erorr':"همچین منوی وجود ندارد"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer= 