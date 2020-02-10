from django.contrib import admin as django_admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

import main.urls, api.urls, admin.urls


urlpatterns = [
    path('', include('main.urls')),
    path('api/', include('api.urls')),
    path('admin/', include('admin.urls')),
    path('django_admin/', django_admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)