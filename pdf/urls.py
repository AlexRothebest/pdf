from django.contrib import admin
from django.urls import path, include

from django.conf import settings

from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import cache_control

import main.urls, api.urls, myadmin.urls


urlpatterns = [
	path('', include('main.urls')),
	path('api/', include('api.urls')),
	path('admin/', include('myadmin.urls')),
	path('django-admin/', admin.site.urls)
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, view=cache_control(no_cache=True, must_revalidate=True)(serve))
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)