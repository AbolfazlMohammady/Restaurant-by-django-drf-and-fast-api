from django.urls import path

from .view import MenuManegement


urlpatterns = [
    path('', MenuManegement.as_view({
        'get': 'list_menu'
    })),
    path('create/', MenuManegement.as_view({
        'post': 'create_menu'
    })),
    path('<int:pk>/', MenuManegement.as_view({
        'get': 'detail_menu'
    })),
]
