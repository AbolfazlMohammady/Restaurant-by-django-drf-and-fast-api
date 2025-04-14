from django.urls import path

from .views import RestaurntViewSet


urlpatterns = [
    path('', RestaurntViewSet.as_view({
        'get': 'list_restaurant'
    })),
    path('<int:pk>/', RestaurntViewSet.as_view({
        'get': 'detail_restaurant',
        'put': 'update_restaurant',
        'delete': 'delete_restaurant',
    })),
    path('create/', RestaurntViewSet.as_view({
        'post': 'create_restaurant'
    })),
    path('<int:restaurant_id>/menu/', RestaurntViewSet.as_view({
        'get': 'list_menu'
    })),
    path('<int:restaurant_id>/menu/<int:menu_id>/', RestaurntViewSet.as_view({
        'get': 'detail_menu'
    })),
]
