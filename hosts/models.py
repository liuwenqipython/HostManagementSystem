import random
import string
import subprocess
import platform
from django.db import models
from django.utils import timezone
from django.conf import settings


class City(models.Model):
    """城市模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='城市名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='城市代码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = '城市'
        ordering = ['name']

    def __str__(self):
        return self.name


class DataCenter(models.Model):
    """机房模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='机房名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='机房代码')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='datacenters', verbose_name='所属城市')
    address = models.CharField(max_length=200, blank=True, verbose_name='机房地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = '机房'
        ordering = ['name']

    def __str__(self):
        return f"{self.city.name} - {self.name}"


class Host(models.Model):
    """主机模型"""
    hostname = models.CharField(max_length=100, unique=True, verbose_name='主机名')
    ip_address = models.GenericIPAddressField(unique=True, verbose_name='IP地址')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hosts', verbose_name='所在城市')
    datacenter = models.ForeignKey(DataCenter, on_delete=models.CASCADE, related_name='hosts', verbose_name='所在机房')
    root_password = models.CharField(max_length=256, verbose_name='Root密码(加密)')
    password_updated_at = models.DateTimeField(auto_now=True, verbose_name='密码更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    description = models.TextField(blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '主机'
        verbose_name_plural = '主机'
        ordering = ['hostname']

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"

    @staticmethod
    def generate_password(length=16):
        """生成随机密码"""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def set_password(self, raw_password):
        """设置并加密密码"""
        from django.contrib.auth.hashers import make_password
        self.root_password = make_password(raw_password)

    def check_password(self, raw_password):
        """验证密码"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.root_password)

    def ping(self):
        """Ping主机检测可达性"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self.ip_address]

        try:
            output = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return output.returncode == 0
        except Exception:
            return False


class PasswordHistory(models.Model):
    """密码历史记录"""
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='password_histories', verbose_name='主机')
    encrypted_password = models.CharField(max_length=256, verbose_name='加密后的密码')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    is_current = models.BooleanField(default=False, verbose_name='是否当前密码')

    class Meta:
        verbose_name = '密码历史'
        verbose_name_plural = '密码历史'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.host.hostname} - {self.changed_at}"


class HostStatistics(models.Model):
    """主机统计数据"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='statistics', verbose_name='城市')
    datacenter = models.ForeignKey(DataCenter, on_delete=models.CASCADE, related_name='statistics', verbose_name='机房')
    host_count = models.IntegerField(default=0, verbose_name='主机数量')
    stat_date = models.DateField(verbose_name='统计日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '主机统计'
        verbose_name_plural = '主机统计'
        unique_together = ['city', 'datacenter', 'stat_date']
        ordering = ['-stat_date', 'city', 'datacenter']

    def __str__(self):
        return f"{self.city.name} - {self.datacenter.name} - {self.stat_date}: {self.host_count}"
