from django.urls import path

from .views import home, client_info


urlpatterns = [
	path('', home),
	path('client/<int:client_id>', client_info)
]