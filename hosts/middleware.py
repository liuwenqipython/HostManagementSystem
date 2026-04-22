
import time
import logging

logger = logging.getLogger('request_time')


class RequestTimeMiddleware:
    """请求耗时统计中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        duration_ms = duration * 1000
        
        log_message = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{request.method} {request.path} "
            f"- {duration_ms:.2f}ms "
            f"- Status: {response.status_code}"
        )
        
        logger.info(log_message)
        
        response['X-Request-Duration'] = f"{duration_ms:.2f}ms"
        
        return response
