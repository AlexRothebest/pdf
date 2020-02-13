from django.db import models
from django.contrib.auth.models import User
from django.contrib import auth


class Client(models.Model):
    name = models.CharField(max_length = 30)
    email = models.EmailField(max_length = 100)

    status = models.CharField(max_length = 30, choices = [('a', 'Admin'), ('u', 'User')])
    account = models.ForeignKey(User, on_delete = models.CASCADE, null = True)

    google_sheet_id = models.CharField(max_length = 100, null = True)
    number_of_parsed_files = models.IntegerField(default = 0)

    def __str__(self):
        return self.name