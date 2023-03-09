
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings

from subscription.views import index


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
