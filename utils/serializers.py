# place for intermediate serializers to avoid circular imports
from rest_framework import serializers
from alert.models import Alert


class SensorDetailAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['message', 'reported_on']
