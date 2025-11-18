from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from utils.serializers import SensorDetailAlertSerializer
from .models import Sensor, Reading


class ReadingIngestSerializer(serializers.Serializer):
    sensor_id = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    flood_m = serializers.FloatField()
    reported_on = serializers.DateTimeField()


class SensorGeoSerializer(GeoFeatureModelSerializer):
    latest_reading = serializers.SerializerMethodField(method_name='get_latest_reading')

    class Meta:
        model = Sensor
        geo_field = 'location'
        fields = ['id', 'name', 'latest_reading']

    def get_latest_reading(self, obj):
        try:
            latest_reading = obj.readings.order_by('-reported_on').first()
            data = {
                "latest_flood_m": latest_reading.flood_m,
                "latest_reported_on": latest_reading.reported_on
                }
        except Exception as e:
            data = {}
        return data


class SensorListGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Sensor
        geo_field = 'location'
        fields = ['id', 'name', 'installed_on', 'is_active']


class ReadingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = ['flood_m', 'reported_on', 'created_on']


class SensorDetailGeoSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Sensor
        geo_field = 'location'
        fields = ['id', 'name', 'installed_on', 'is_active']
