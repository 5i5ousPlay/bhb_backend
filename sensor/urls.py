from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ingest_reading, LiveSensorViewSet, SensorListView, SensorDetailView

router = DefaultRouter()
router.register("live-sensors", LiveSensorViewSet, basename="live-sensors")

urlpatterns = [
    path('list/', SensorListView.as_view(), name='sensor-list'),
    path('detail/<str:id>/', SensorDetailView.as_view(), name='sensor-detail'),
    path('ingest/', ingest_reading, name='sensor-ingest'),
    path("", include(router.urls)),
    ]