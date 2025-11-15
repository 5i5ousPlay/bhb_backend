import uuid
from django.contrib.gis.db import models
from django.utils import timezone


class Sensor(models.Model):
    id = models.CharField(editable=False, primary_key=True)
    name = models.CharField(max_length=128, blank=True)
    location = models.PointField(srid=4326, blank=True, null=True)
    installed_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class Reading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    flood_m = models.FloatField()
    reported_on = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['reported_on']),
            models.Index(fields=['sensor', 'reported_on'])
            ]
        get_latest_by = "reported_on"
