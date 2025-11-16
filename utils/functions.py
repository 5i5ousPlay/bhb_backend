from datetime import timedelta
from django.utils import timezone
from sensor.models import Reading
from alert.models import Alert

LEVEL_NORMAL = "NORMAL"
LEVEL_ELEVATED = "ELEVATED"
LEVEL_WARNING = "WARNING"
LEVEL_CRITICAL = "CRITICAL"


def classify_level(h):
    if h >= 0.7:
        return LEVEL_CRITICAL
    elif h >= 0.3:
        return LEVEL_WARNING
    elif h >= 0.1:
        return LEVEL_ELEVATED
    else:
        return LEVEL_NORMAL


def evaluate_alerts(reading):
    sensor = reading.sensor

    prev = (
        Reading.objects
        .filter(sensor=sensor, reported_on__lt=reading.reported_on)
        .order_by("-reported_on")
        .first()
    )

    alerts_to_create = []

    new_level = classify_level(reading.flood_m)
    prev_level = classify_level(prev.flood_m) if prev else LEVEL_NORMAL

    if new_level != prev_level:
        msg = f"{new_level.capitalize()} flood level reached ({reading.flood_m:.2f} m)"
        alerts_to_create.append({
            "kind": "LEVEL_CHANGE",
            "message": msg,
        })

    if prev:
        delta_h = reading.flood_m - prev.flood_m
        delta_t = (reading.reported_on - prev.reported_on).total_seconds()

        if delta_h > 0.10 and delta_t <= 60:
            # check last rapid-rise alert for this sensor
            cooldown = timedelta(minutes=5)
            now = timezone.now()
            last_rapid = (
                Alert.objects
                .filter(sensor=sensor, kind="RAPID_RISE")
                .order_by("-reported_on")
                .first()
            )

            can_alert = (
                not last_rapid or
                (now - last_rapid.reported_on) > cooldown or
                reading.flood_m - last_rapid.reading.flood_m > 0.10
            )

            if can_alert:
                alerts_to_create.append({
                    "kind": "RAPID_RISE",
                    "message": f"Rapid rise detected (+{delta_h:.2f} m in {delta_t:.0f}s)",
                })

    for a in alerts_to_create:
        Alert.objects.create(
            sensor=sensor,
            reading=reading,
            kind=a["kind"],
            message=a["message"],
            )
