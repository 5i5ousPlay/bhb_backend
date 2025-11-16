from django.urls import path
from .views import summary_view, recent_alerts, flood_level_trend

urlpatterns = [
    path('summary/', summary_view, name='dashboard-summary'),
    path('recent-alerts/', recent_alerts, name='dashboard-alerts'),
    path('flood-trend/', flood_level_trend, name='dashboard-ftrend'),
    ]
