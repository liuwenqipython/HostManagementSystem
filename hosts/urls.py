from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CityViewSet, DataCenterViewSet, HostViewSet,
    PasswordHistoryViewSet, HostStatisticsViewSet
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'datacenters', DataCenterViewSet, basename='datacenter')
router.register(r'hosts', HostViewSet, basename='host')
router.register(r'password-histories', PasswordHistoryViewSet, basename='password-history')
router.register(r'statistics', HostStatisticsViewSet, basename='statistics')

urlpatterns = [
    path('', include(router.urls)),
]
