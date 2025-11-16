from datetime import timedelta
from django.utils import timezone
from django.db.models import Prefetch, Avg
from django.db.models.functions import TruncHour, TruncMinute
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from sensor.models import Sensor, Reading
from alert.models import Alert
from alert.serializers import AlertSerializer


MODES = ['hour', 'minute']


@api_view(['GET'])
def summary_view(request):
    reading_qs = Reading.objects.order_by('-reported_on')
    sensors = (
        Sensor.objects
        .prefetch_related(
            Prefetch('readings', queryset=reading_qs, to_attr='ordered_readings')
            )
        )

    total_sensors = sensors.count()
    online_sensors = sensors.filter(is_active=True).count()

    flooded_sensors = 0
    critical_sensors = 0

    flood_severity_dist = {
        "no_flood": 0,
        "minor": 0,
        "moderate": 0,
        "severe": 0,
        "extreme": 0,
        }

    for s in sensors:
        # handle sensors with no readings yet
        if not s.ordered_readings:
            flood_severity_dist["no_flood"] += 1
            continue

        r = s.ordered_readings[0].flood_m  # latest reading

        if r > 1.0:
            flood_severity_dist['extreme'] += 1
        elif r >= 0.7:
            critical_sensors += 1
            flood_severity_dist['severe'] += 1
        elif r >= 0.3:
            flood_severity_dist['moderate'] += 1
        elif r >= 0.1:
            flooded_sensors += 1
            flood_severity_dist['minor'] += 1
        else:
            flood_severity_dist['no_flood'] += 1

    date_from = timezone.now() - timedelta(hours=24)
    alerts_last_24hrs = Alert.objects.filter(reported_on__gte=date_from).count()

    summary = {
        "total": total_sensors,
        "online": online_sensors,
        "flooded": flooded_sensors,
        "critical": critical_sensors,
        "alerts_24hrs": alerts_last_24hrs,
        }

    payload = {
        "summary": summary,
        "flood_severity": flood_severity_dist,
        }

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
def recent_alerts(request):
    alerts = Alert.objects.all()[:10]
    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def flood_level_trend(request):
    mode = request.query_params.get("mode", "hour")

    if mode not in MODES:
        return Response({"error": "Invalid mode"}, status=400)

    now = timezone.now()

    # Filter by window
    if mode == 'hour':
        date_from = now - timedelta(hours=24)
        trunc_fn = TruncHour
    else:  # minute
        date_from = now - timedelta(minutes=60)
        trunc_fn = TruncMinute

    readings = (
        Reading.objects
        .filter(reported_on__gte=date_from)
        .annotate(ts=trunc_fn('reported_on'))  # truncate datetime
        .values('ts')  # group by truncated timestamp
        .annotate(avg_flood=Avg('flood_m'))  # average flood level
        .order_by('ts')  # chronological order
    )

    return Response(list(readings), status=status.HTTP_200_OK)
