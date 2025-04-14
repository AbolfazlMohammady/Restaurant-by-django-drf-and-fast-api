from django.urls import path

from .views import ProfileViewSet

urlpatterns = [
    path('me/', ProfileViewSet.as_view({
        'get': 'retreive',
        'patch': 'update',
    })),
    path('change_password/', ProfileViewSet.as_view({
        'post': 'change_password',
    })),
    path('delete_account/', ProfileViewSet.as_view({
        'post': 'delete_account',
    })),
]
