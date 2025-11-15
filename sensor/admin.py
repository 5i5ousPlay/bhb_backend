from django.contrib import admin
from .models import Sensor, Reading

# Register your models here.
admin.site.register(Sensor)
admin.site.register(Reading)
