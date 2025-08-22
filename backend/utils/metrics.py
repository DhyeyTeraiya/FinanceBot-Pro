"""
Performance metrics and monitoring utilities
"""
import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class RequestMetrics:
    """Metrics for individual requests"""
    endpoint: str
    method: str
    status_code: int
    duration: float
    timestamp: datetime
    user_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AIMetrics:
    """Metrics for AI interactions"""
    session_id: str
    model: str
    message_length: int
    response_length: int
    duration: float
    timestamp: datetime
    success: bool = True
    error: Optional[str] = None


class MetricsCollector:
    """Collect and analyze application metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_metrics: deque = deque(maxlen=max_history)
        self.ai_metrics: deque = deque(maxlen=max_history)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.endpoint_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0,
            'errors': 0
        })
    
    def record_request(self, metrics: RequestMetrics):
        """Record request metrics"""
        self.request_metrics.append(metrics)
        
        # Update endpoint statistics
        endpoint_key = f"{metrics.method} {metrics.endpoint}"
        stats = self.endpoint_stats[endpoint_key]
        stats['count'] += 1
        stats['total_duration'] += metrics.duration
        stats['avg_duration'] = stats['total_duration'] / stats['count']
        
        if metrics.status_code >= 400:
            stats['errors'] += 1
            if metrics.error:
                self.error_counts[metrics.error] += 1
    
    def record_ai_interaction(self, metrics: AIMetrics):
        """Record AI interaction metrics"""
        self.ai_metrics.append(metrics)
        
        if not metrics.success and metrics.error:
            self.error_counts[f"AI_{metrics.error}"] += 1
    
    def get_request_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get request statistics for the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_requests = [
            m for m in self.request_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_requests:
            return {
                'total_requests': 0,
                'avg_duration': 0.0,
                'error_rate': 0.0,
                'requests_per_minute': 0.0
            }
        
        total_requests = len(recent_requests)
        total_duration = sum(m.duration for m in recent_requests)
        error_count = sum(1 for m in recent_requests if m.status_code >= 400)
        
        return {
            'total_requests': total_requests,
            'avg_duration': total_duration / total_requests,
            'error_rate': error_count / total_requests,
            'requests_per_minute': total_requests / minutes,
            'status_codes': self._count_status_codes(recent_requests)
        }
    
    def get_ai_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get AI interaction statistics for the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_ai = [
            m for m in self.ai_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_ai:
            return {
                'total_interactions': 0,
                'avg_duration': 0.0,
                'success_rate': 0.0,
                'avg_message_length': 0.0,
                'avg_response_length': 0.0
            }
        
        total_interactions = len(recent_ai)
        successful_interactions = sum(1 for m in recent_ai if m.success)
        total_duration = sum(m.duration for m in recent_ai)
        total_message_length = sum(m.message_length for m in recent_ai)
        total_response_length = sum(m.response_length for m in recent_ai)
        
        return {
            'total_interactions': total_interactions,
            'avg_duration': total_duration / total_interactions,
            'success_rate': successful_interactions / total_interactions,
            'avg_message_length': total_message_length / total_interactions,
            'avg_response_length': total_response_length / total_interactions,
            'models_used': list(set(m.model for m in recent_ai))
        }
    
    def get_top_errors(self, limit: int = 10) -> Dict[str, int]:
        """Get top errors by frequency"""
        return dict(sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit])
    
    def get_endpoint_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics by endpoint"""
        return dict(self.endpoint_stats)
    
    def _count_status_codes(self, requests: list) -> Dict[int, int]:
        """Count status codes in request list"""
        status_counts = defaultdict(int)
        for request in requests:
            status_counts[request.status_code] += 1
        return dict(status_counts)
    
    def reset_metrics(self):
        """Reset all collected metrics"""
        self.request_metrics.clear()
        self.ai_metrics.clear()
        self.error_counts.clear()
        self.endpoint_stats.clear()


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
    
    def get_duration(self) -> float:
        """Get operation duration in seconds"""
        return self.duration or 0.0


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return metrics_collector