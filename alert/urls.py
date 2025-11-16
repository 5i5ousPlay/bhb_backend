from django.urls import path
from .views import AlertListView

urlpatterns = [
    path('list/', AlertListView.as_view(), name='alert-list'),
    ]
