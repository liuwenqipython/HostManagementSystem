"""
初始化测试数据脚本
运行: python init_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HostManagementSystem.settings')
django.setup()

from hosts.models import City, DataCenter, Host


def init_data():
    print("开始初始化测试数据...")

    cities_data = [
        {'name': '北京', 'code': 'BJ'},
        {'name': '上海', 'code': 'SH'},
        {'name': '广州', 'code': 'GZ'},
        {'name': '深圳', 'code': 'SZ'},
    ]

    cities = []
    for city_data in cities_data:
        city, created = City.objects.get_or_create(
            code=city_data['code'],
            defaults=city_data
        )
        cities.append(city)
        if created:
            print(f"创建城市: {city.name}")

    datacenters_data = [
        {'city_code': 'BJ', 'name': '北京机房A', 'code': 'BJ-A', 'address': '北京市朝阳区xxx'},
        {'city_code': 'BJ', 'name': '北京机房B', 'code': 'BJ-B', 'address': '北京市海淀区xxx'},
        {'city_code': 'SH', 'name': '上海机房A', 'code': 'SH-A', 'address': '上海市浦东新区xxx'},
        {'city_code': 'GZ', 'name': '广州机房A', 'code': 'GZ-A', 'address': '广州市天河区xxx'},
        {'city_code': 'SZ', 'name': '深圳机房A', 'code': 'SZ-A', 'address': '深圳市南山区xxx'},
    ]

    datacenters = []
    for dc_data in datacenters_data:
        city = City.objects.get(code=dc_data.pop('city_code'))
        dc, created = DataCenter.objects.get_or_create(
            code=dc_data['code'],
            defaults={'city': city, **dc_data}
        )
        datacenters.append(dc)
        if created:
            print(f"创建机房: {dc.name}")

    hosts_data = [
        {'hostname': 'bj-web-01', 'ip': '192.168.1.10', 'city_code': 'BJ', 'dc_code': 'BJ-A'},
        {'hostname': 'bj-web-02', 'ip': '192.168.1.11', 'city_code': 'BJ', 'dc_code': 'BJ-A'},
        {'hostname': 'bj-db-01', 'ip': '192.168.1.20', 'city_code': 'BJ', 'dc_code': 'BJ-B'},
        {'hostname': 'sh-web-01', 'ip': '192.168.2.10', 'city_code': 'SH', 'dc_code': 'SH-A'},
        {'hostname': 'sh-web-02', 'ip': '192.168.2.11', 'city_code': 'SH', 'dc_code': 'SH-A'},
        {'hostname': 'gz-web-01', 'ip': '192.168.3.10', 'city_code': 'GZ', 'dc_code': 'GZ-A'},
        {'hostname': 'sz-web-01', 'ip': '192.168.4.10', 'city_code': 'SZ', 'dc_code': 'SZ-A'},
    ]

    for host_data in hosts_data:
        city = City.objects.get(code=host_data.pop('city_code'))
        dc = DataCenter.objects.get(code=host_data.pop('dc_code'))

        hostname = host_data.pop('hostname')
        ip = host_data.pop('ip')

        host, created = Host.objects.get_or_create(
            hostname=hostname,
            defaults={
                'ip_address': ip,
                'city': city,
                'datacenter': dc,
                'description': f'{hostname} 测试主机'
            }
        )

        if created:
            password = Host.generate_password()
            host.set_password(password)
            host.save()

            from hosts.models import PasswordHistory
            PasswordHistory.objects.create(
                host=host,
                encrypted_password=host.root_password,
                is_current=True
            )

            print(f"创建主机: {hostname} ({ip}), 密码: {password}")
        else:
            print(f"主机已存在: {hostname}")

    print("\n测试数据初始化完成!")
    print(f"城市数量: {City.objects.count()}")
    print(f"机房数量: {DataCenter.objects.count()}")
    print(f"主机数量: {Host.objects.count()}")


if __name__ == '__main__':
    init_data()
