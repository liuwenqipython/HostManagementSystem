import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import City, DataCenter, Host, PasswordHistory, HostStatistics
from .serializers import (
    CitySerializer, DataCenterSerializer, HostSerializer,
    PasswordHistorySerializer, HostStatisticsSerializer
)

logger = logging.getLogger(__name__)


class CityViewSet(viewsets.ModelViewSet):
    """城市视图集"""
    queryset = City.objects.all()
    serializer_class = CitySerializer


class DataCenterViewSet(viewsets.ModelViewSet):
    """机房视图集"""
    queryset = DataCenter.objects.all()
    serializer_class = DataCenterSerializer


class HostViewSet(viewsets.ModelViewSet):
    """主机视图集"""
    queryset = Host.objects.all()
    serializer_class = HostSerializer

    @action(detail=True, methods=['get'])
    def ping(self, request, pk=None):
        """Ping主机检测可达性"""
        host = self.get_object()
        is_reachable = host.ping()

        return Response({
            'hostname': host.hostname,
            'ip_address': host.ip_address,
            'is_reachable': is_reachable,
            'message': '主机可达' if is_reachable else '主机不可达'
        })

    @action(detail=False, methods=['get'])
    def ping_all(self, request):
        """Ping所有活跃主机"""
        hosts = Host.objects.filter(is_active=True)
        results = []

        for host in hosts:
            is_reachable = host.ping()
            results.append({
                'hostname': host.hostname,
                'ip_address': host.ip_address,
                'is_reachable': is_reachable
            })

        return Response(results)


class PasswordHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """密码历史视图集(只读)"""
    queryset = PasswordHistory.objects.all()
    serializer_class = PasswordHistorySerializer


class HostStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """主机统计视图集(只读)"""
    queryset = HostStatistics.objects.all()
    serializer_class = HostStatisticsSerializer

    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """按日期查询统计数据"""
        date = request.query_params.get('date')
        if date:
            statistics = HostStatistics.objects.filter(stat_date=date)
        else:
            statistics = HostStatistics.objects.order_by('-stat_date')[:10]

        serializer = self.get_serializer(statistics, many=True)
        return Response(serializer.data)
