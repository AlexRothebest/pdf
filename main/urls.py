from django.urls import path

from .views import home, login, add_user, registration, restore_password, load_pdf

urlpatterns = [
    path('', home),
    path('login/', login),
    path('add_user/', add_user),
    path('registration/', registration),
    path('restore_password/', restore_password),

    path('load_pdf/', load_pdf)
]