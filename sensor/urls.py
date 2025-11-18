from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ingest_reading, LiveSensorViewSet, SensorListView,
                    SensorDetailView, sensor_detail_alert_view, sensor_detail_reading_view)

router = DefaultRouter()
router.register("live-sensors", LiveSensorViewSet, basename="live-sensors")

urlpatterns = [
    path('list/', SensorListView.as_view(), name='sensor-list'),
    path('detail/<str:id>/', SensorDetailView.as_view(), name='sensor-detail'),
    path('detail/<str:id>/readings/', sensor_detail_reading_view, name='sensor-detail-readings'),
    path('detail/<str:id>/alerts/', sensor_detail_alert_view, name='sensor-detail-alerts'),
    path('ingest/', ingest_reading, name='sensor-ingest'),
    path("", include(router.urls)),
    ]