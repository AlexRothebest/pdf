from django.urls import path

from .views import home, login, add_user, registration, load_pdf,\
				   restore_password, change_password

urlpatterns = [
	path('', home),
	path('login/', login),
	path('add-user/', add_user),
	path('registration/', registration),
	path('restore-password/', restore_password),
	path('change-password/', change_password),

	path('load-pdf/', load_pdf)
]