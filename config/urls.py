from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/docs/schema' , SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/schema/ui' , SpectacularSwaggerView.as_view()),
    path('api/core/', include('core.urls')),
    path('api/restaurant/', include('restaurant.urls')),
    path('api/management/menu/', include('management.menu.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))