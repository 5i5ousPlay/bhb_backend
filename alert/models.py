from django.db import models
from sensor.models import Sensor, Reading


# Create your models here.
class Alert(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='alerts')
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name='alerts')
    kind = models.CharField(max_length=32)
    message = models.CharField(max_length=255)
    reported_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reported_on']