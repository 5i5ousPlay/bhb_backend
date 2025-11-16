from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from sensor.models import Sensor


@shared_task
def update_sensor_status():
    threshold = timezone.now() - timedelta(minutes=60)

    # Mark offline sensors
    Sensor.objects.filter(last_seen__lt=threshold).update(is_active=False)

    # Mark sensors back online (optional)
    Sensor.objects.filter(last_seen__gte=threshold).update(is_active=True)
