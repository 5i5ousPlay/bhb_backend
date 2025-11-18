import json
import uuid
from django.shortcuts import render
from django.utils import timezone
from django.db.models import OuterRef, Subquery, F
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point
from rest_framework import status, permissions, viewsets, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter, DistanceToPointFilter
from utils.functions import evaluate_alerts
from utils.serializers import SensorDetailAlertSerializer
from alert.models import Alert

from .models import Sensor, Reading
from .serializers import (ReadingIngestSerializer, ReadingDetailSerializer, SensorGeoSerializer,
                          SensorListGeoSerializer, SensorDetailGeoSerializer)


@api_view(['POST'])
def ingest_reading(request):
    serializer = ReadingIngestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        with transaction.atomic():
            sensor, _ = Sensor.objects.get_or_create(
                id=data['sensor_id']
                )
            sensor.location=Point(data['lon'], data['lat'])
            sensor.is_active = True
            sensor.last_seen = timezone.now()
            sensor.save(update_fields=['location', 'is_active', 'last_seen'])

            reading = Reading.objects.create(
                sensor=sensor,
                flood_m=data['flood_m'],
                reported_on=data['reported_on']
                )

            evaluate_alerts(reading=reading)
    except Exception as e:
        return Response({"Bad Request": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"ok": True}, status=status.HTTP_201_CREATED)


class LiveSensorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SensorGeoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Sensor.objects.filter(is_active=True)


class SensorListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page-size"
    max_page_size = 20


class SensorListView(generics.ListAPIView):
    queryset = Sensor.objects.order_by("-installed_on")
    serializer_class = SensorListGeoSerializer
    pagination_class = SensorListPagination
    filter_backends = [filters.SearchFilter, InBBoxFilter, DistanceToPointFilter]
    bbox_filter_field = 'location'
    distance_filter_field = 'location'
    distance_filter_convert_meters = True
    search_fields = ['id', 'name']


class SensorDetailView(generics.RetrieveAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorDetailGeoSerializer
    lookup_field = 'id'


@api_view(['GET'])
def sensor_detail_reading_view(request, id):
    sensor = get_object_or_404(Sensor, id=id)
    readings = Reading.objects.filter(sensor=sensor)  # or sensor_id=id
    serializer = ReadingDetailSerializer(readings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def sensor_detail_alert_view(request, id):
    sensor = get_object_or_404(Sensor, id=id)
    alerts = Alert.objects.filter(sensor=sensor)
    serializer = SensorDetailAlertSerializer(alerts, many=True)
    return Response(serializer.data)
