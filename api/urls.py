from django.contrib import admin
from django.urls import path

from .views import login, logout, add_user, restore_password, parse_pdf_file, change_clients_data


urlpatterns = [
	path('login/', login),
	path('logout/', logout),
	path('add_user/', add_user),
	path('restore_password/', restore_password),

	path('change-clients-data', change_clients_data),

	path('parse_pdf/', parse_pdf_file)
]