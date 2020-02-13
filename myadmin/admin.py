from django.contrib import admin

from .models import ParsedData, Vehicle


admin.site.register(ParsedData)
admin.site.register(Vehicle)