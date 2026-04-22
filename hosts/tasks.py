import logging
from celery import shared_task
from django.utils import timezone
from datetime import date
from django.db.models import Count
from .models import Host, PasswordHistory, HostStatistics

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def change_host_passwords_task(self):
    """定时任务：每8小时修改所有主机的密码"""
    logger.info("开始执行密码修改任务")
    
    hosts = Host.objects.filter(is_active=True)
    updated_count = 0
    
    for host in hosts:
        try:
            old_password_record = PasswordHistory.objects.filter(
                host=host, is_current=True
            ).first()
            
            new_password = Host.generate_password()
            host.set_password(new_password)
            host.save()
            
            if old_password_record:
                old_password_record.is_current = False
                old_password_record.save()
            
            PasswordHistory.objects.create(
                host=host,
                encrypted_password=host.root_password,
                is_current=True
            )
            
            updated_count += 1
            logger.info(f"主机 {host.hostname} 密码已更新")
            
        except Exception as e:
            logger.error(f"更新主机 {host.hostname} 密码失败: {str(e)}")
            continue
    
    logger.info(f"密码修改任务完成，共更新 {updated_count} 台主机")
    return {'updated_count': updated_count}


@shared_task(bind=True, max_retries=3)
def daily_statistics_task(self):
    """定时任务：每天00:00统计各城市机房的主机数量"""
    logger.info("开始执行主机统计任务")
    
    yesterday = date.today()
    
    stats_data = (
        Host.objects.filter(is_active=True)
        .values('city', 'datacenter')
        .annotate(count=Count('id'))
    )
    
    created_count = 0
    for stat in stats_data:
        HostStatistics.objects.update_or_create(
            city_id=stat['city'],
            datacenter_id=stat['datacenter'],
            stat_date=yesterday,
            defaults={'host_count': stat['count']}
        )
        created_count += 1
    
    logger.info(f"主机统计任务完成，共统计 {created_count} 条记录")
    return {'created_count': created_count}
