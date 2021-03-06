from django.contrib import admin
from django.urls import path

from .views import login, logout, add_user, restore_password, change_password, parse_pdf_file,\
				   change_clients_data, delete_clients, download_clients_parsed_data,\
				   add_new_googlesheet


urlpatterns = [
	path('login', login),
	path('logout', logout),
	path('add-user', add_user),
	path('restore-password', restore_password),
	path('change-password', change_password),

	path('delete-clients', delete_clients),
	path('change-clients-data', change_clients_data),

	path('add-new-googlesheet', add_new_googlesheet),

	path('parse-pdf', parse_pdf_file),

	path('download-clients-parsed-data', download_clients_parsed_data)
]