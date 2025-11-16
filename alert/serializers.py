from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Alert
from sensor.serializers import ReadingDetailSerializer
from sensor.models import Sensor


class AlertSensorGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Sensor
        geo_field = 'location'
        fields = ['id', 'name', 'installed_on', 'is_active']


class AlertSerializer(serializers.ModelSerializer):
    reading = ReadingDetailSerializer(read_only=True)
    sensor = AlertSensorGeoSerializer(read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'sensor', 'reading', 'message', 'reported_on']
