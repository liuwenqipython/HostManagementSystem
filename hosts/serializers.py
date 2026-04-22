
from rest_framework import serializers
from .models import City, DataCenter, Host, PasswordHistory, HostStatistics


class CitySerializer(serializers.ModelSerializer):
    """城市序列化器"""
    class Meta:
        model = City
        fields = ['id', 'name', 'code', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class DataCenterSerializer(serializers.ModelSerializer):
    """机房序列化器"""
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = DataCenter
        fields = ['id', 'name', 'code', 'city', 'city_name', 'address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class HostSerializer(serializers.ModelSerializer):
    """主机序列化器"""
    city_name = serializers.CharField(source='city.name', read_only=True)
    datacenter_name = serializers.CharField(source='datacenter.name', read_only=True)

    class Meta:
        model = Host
        fields = [
            'id', 'hostname', 'ip_address', 'city', 'city_name',
            'datacenter', 'datacenter_name', 'root_password',
            'password_updated_at', 'is_active', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['root_password', 'password_updated_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'root_password': {'write_only': True}
        }

    def create(self, validated_data):
        raw_password = validated_data.pop('root_password', None)
        if not raw_password:
            raw_password = Host.generate_password()
        
        host = Host(**validated_data)
        host.set_password(raw_password)
        host.save()
        
        PasswordHistory.objects.create(
            host=host,
            encrypted_password=host.root_password,
            is_current=True
        )
        
        return host

    def update(self, instance, validated_data):
        raw_password = validated_data.pop('root_password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if raw_password:
            instance.set_password(raw_password)
            instance.save()
            
            PasswordHistory.objects.filter(host=instance).update(is_current=False)
            PasswordHistory.objects.create(
                host=instance,
                encrypted_password=instance.root_password,
                is_current=True
            )
        else:
            instance.save()
        
        return instance


class PasswordHistorySerializer(serializers.ModelSerializer):
    """密码历史序列化器"""
    hostname = serializers.CharField(source='host.hostname', read_only=True)

    class Meta:
        model = PasswordHistory
        fields = ['id', 'host', 'hostname', 'encrypted_password', 'changed_at', 'is_current']
        read_only_fields = ['encrypted_password', 'changed_at']


class HostStatisticsSerializer(serializers.ModelSerializer):
    """主机统计序列化器"""
    city_name = serializers.CharField(source='city.name', read_only=True)
    datacenter_name = serializers.CharField(source='datacenter.name', read_only=True)

    class Meta:
        model = HostStatistics
        fields = ['id', 'city', 'city_name', 'datacenter', 'datacenter_name', 
                  'host_count', 'stat_date', 'created_at']
        read_only_fields = ['created_at']
