from django.db import models
from django.contrib.auth.models import User
from django.contrib import auth


class Client(models.Model):
    name = models.CharField(max_length = 30, null=True)
    email = models.EmailField(max_length = 100, null=True)

    status = models.CharField(max_length = 30, choices = [('a', 'Admin'), ('u', 'User')], null=True)
    account = models.ForeignKey(User, on_delete = models.CASCADE, null=True)

    google_sheet_id = models.CharField(max_length = 100, null = True)
    number_of_parsed_files = models.IntegerField(default = 0)

    next_row_to_write_data = models.IntegerField(default = 2)

    def __str__(self):
        return self.name