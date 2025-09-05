"""
Performance Monitoring for WaveSpeed AI Application

Simple performance monitoring and metrics collection.
"""

import time
import psutil
from typing import Dict, Any
from logger import get_logger

logger = get_logger()


class PerformanceMonitor:
    """Simple performance monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}
        self.task_timers = {}
    
    def start_task_timer(self, task_name: str):
        """Start timing a task"""
        self.task_timers[task_name] = time.time()
        logger.debug(f"Started timing task: {task_name}")
    
    def end_task_timer(self, task_name: str) -> float:
        """End timing a task and return duration"""
        if task_name not in self.task_timers:
            logger.warning(f"No timer found for task: {task_name}")
            return 0.0
        
        duration = time.time() - self.task_timers[task_name]
        del self.task_timers[task_name]
        
        # Store metric
        if 'task_durations' not in self.metrics:
            self.metrics['task_durations'] = {}
        self.metrics['task_durations'][task_name] = duration
        
        logger.debug(f"Task '{task_name}' completed in {duration:.2f}s")
        return duration
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'uptime_seconds': time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}
    
    def log_system_status(self):
        """Log current system status"""
        try:
            metrics = self.get_system_metrics()
            logger.info(f"System Status - CPU: {metrics.get('cpu_percent', 'N/A')}%, "
                       f"Memory: {metrics.get('memory_percent', 'N/A')}%, "
                       f"Uptime: {metrics.get('uptime_seconds', 0):.1f}s")
        except Exception as e:
            logger.error(f"Failed to log system status: {str(e)}")
    
    def get_performance_summary(self) -> str:
        """Get performance summary as string"""
        try:
            system_metrics = self.get_system_metrics()
            uptime = system_metrics.get('uptime_seconds', 0)
            
            summary = f"Performance Summary:\n"
            summary += f"  Uptime: {uptime:.1f} seconds\n"
            summary += f"  CPU Usage: {system_metrics.get('cpu_percent', 'N/A')}%\n"
            summary += f"  Memory Usage: {system_metrics.get('memory_percent', 'N/A')}%\n"
            
            if 'task_durations' in self.metrics:
                summary += f"  Task Durations:\n"
                for task, duration in self.metrics['task_durations'].items():
                    summary += f"    {task}: {duration:.2f}s\n"
            
            return summary
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {str(e)}")
            return "Performance summary unavailable"


# Global performance monitor
perf_monitor = PerformanceMonitor()


def get_performance_monitor():
    """Get the global performance monitor"""
    return perf_monitor
