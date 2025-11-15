from django.shortcuts import render
from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from .models import Alert
from .serializers import AlertSerializer


class AlertListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page-size'
    max_page_size = 20


# Create your views here.
class AlertListView(generics.ListAPIView):
    queryset = Alert.objects.order_by("-reported_on")
    serializer_class = AlertSerializer
    pagination_class = AlertListPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['message', 'reported_on', 'sensor__id']
