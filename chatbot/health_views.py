"""
Health check and monitoring endpoints
"""
import os
import time
import psutil
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class HealthCheckView(APIView):
    """
    Basic health check endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return basic health status
        """
        return Response({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0'
        })

class DetailedHealthView(APIView):
    """
    Detailed health check with system metrics
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return detailed health information
        """
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'checks': {}
        }
        
        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data['checks']['database'] = {
                'status': 'healthy',
                'response_time': 0
            }
        except Exception as e:
            health_data['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'unhealthy'
        
        # Cache check
        try:
            cache.set('health_check', 'ok', 10)
            cache_result = cache.get('health_check')
            if cache_result == 'ok':
                health_data['checks']['cache'] = {
                    'status': 'healthy'
                }
            else:
                health_data['checks']['cache'] = {
                    'status': 'unhealthy',
                    'error': 'Cache test failed'
                }
                health_data['status'] = 'unhealthy'
        except Exception as e:
            health_data['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'unhealthy'
        
        # Disk space check
        try:
            disk_usage = psutil.disk_usage('/')
            free_space_gb = disk_usage.free / (1024**3)
            total_space_gb = disk_usage.total / (1024**3)
            free_percentage = (disk_usage.free / disk_usage.total) * 100
            
            health_data['checks']['disk'] = {
                'status': 'healthy' if free_percentage > 10 else 'warning',
                'free_space_gb': round(free_space_gb, 2),
                'total_space_gb': round(total_space_gb, 2),
                'free_percentage': round(free_percentage, 2)
            }
            
            if free_percentage <= 5:
                health_data['status'] = 'unhealthy'
            elif free_percentage <= 10:
                health_data['status'] = 'warning'
                
        except Exception as e:
            health_data['checks']['disk'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'unhealthy'
        
        # Memory check
        try:
            memory = psutil.virtual_memory()
            health_data['checks']['memory'] = {
                'status': 'healthy' if memory.percent < 90 else 'warning',
                'used_percentage': memory.percent,
                'available_gb': round(memory.available / (1024**3), 2)
            }
            
            if memory.percent >= 95:
                health_data['status'] = 'unhealthy'
            elif memory.percent >= 90:
                health_data['status'] = 'warning'
                
        except Exception as e:
            health_data['checks']['memory'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'unhealthy'
        
        # Vector store directory check
        try:
            vector_store_dir = getattr(settings, 'VECTOR_STORE_DIR', None)
            if vector_store_dir and os.path.exists(vector_store_dir):
                health_data['checks']['vector_store'] = {
                    'status': 'healthy',
                    'path': vector_store_dir
                }
            else:
                health_data['checks']['vector_store'] = {
                    'status': 'warning',
                    'message': 'Vector store directory not found or not configured'
                }
        except Exception as e:
            health_data['checks']['vector_store'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        return Response(health_data)

class MetricsView(APIView):
    """
    System metrics endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return system metrics
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process information
            process = psutil.Process()
            
            metrics = {
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory': {
                        'total_gb': round(memory.total / (1024**3), 2),
                        'available_gb': round(memory.available / (1024**3), 2),
                        'used_percent': memory.percent
                    },
                    'disk': {
                        'total_gb': round(disk.total / (1024**3), 2),
                        'free_gb': round(disk.free / (1024**3), 2),
                        'used_percent': round((disk.used / disk.total) * 100, 2)
                    }
                },
                'process': {
                    'pid': process.pid,
                    'memory_mb': round(process.memory_info().rss / (1024**2), 2),
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads()
                }
            }
            
            return Response(metrics)
            
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return Response({
                'error': 'Failed to get metrics',
                'message': str(e)
            }, status=500)

class ReadinessView(APIView):
    """
    Readiness probe endpoint for Kubernetes
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Check if the application is ready to serve requests
        """
        try:
            # Check database connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Check cache connectivity
            cache.set('readiness_check', 'ok', 10)
            cache_result = cache.get('readiness_check')
            
            if cache_result == 'ok':
                return Response({'status': 'ready'})
            else:
                return Response({'status': 'not ready', 'reason': 'Cache not available'}, status=503)
                
        except Exception as e:
            logger.error(f"Readiness check failed: {str(e)}")
            return Response({
                'status': 'not ready',
                'reason': str(e)
            }, status=503)

class LivenessView(APIView):
    """
    Liveness probe endpoint for Kubernetes
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Check if the application is alive
        """
        return Response({'status': 'alive'})
