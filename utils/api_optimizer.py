"""API Usage Optimizer for I2POC Application"""

import time
import hashlib
import logging
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, deque
from threading import Lock

logger = logging.getLogger(__name__)


class APIOptimizer:
    """Optimizes API usage through batching, deduplication, and rate limiting"""
    
    def __init__(self):
        self.request_history = defaultdict(deque)
        self.deduplication_cache = {}
        self.batch_queues = defaultdict(list)
        self.rate_limits = {
            'default': {'max_requests': 10, 'time_window': 60},  # 10 requests per minute
            'research': {'max_requests': 5, 'time_window': 30},  # 5 requests per 30 seconds
            'financial': {'max_requests': 3, 'time_window': 60},  # 3 requests per minute
        }
        self.lock = Lock()
        self.usage_stats = {
            'total_requests': 0,
            'batched_requests': 0,
            'deduplicated_requests': 0,
            'rate_limited_requests': 0,
            'api_costs_saved': 0  # Estimated cost savings
        }
    
    def generate_request_hash(self, endpoint: str, params: Dict) -> str:
        """Generate a unique hash for a request to detect duplicates"""
        param_string = str(sorted(params.items()))
        request_string = f"{endpoint}:{param_string}"
        return hashlib.md5(request_string.encode()).hexdigest()
    
    def check_duplicate(self, endpoint: str, params: Dict, cache_ttl: int = 300) -> bool:
        """
        Check if a request is a duplicate within the cache TTL
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            cache_ttl: Time to live for duplicate cache in seconds
            
        Returns:
            True if duplicate, False otherwise
        """
        request_hash = self.generate_request_hash(endpoint, params)
        current_time = time.time()
        
        with self.lock:
            if request_hash in self.deduplication_cache:
                cache_time = self.deduplication_cache[request_hash]
                if current_time - cache_time < cache_ttl:
                    self.usage_stats['deduplicated_requests'] += 1
                    self.usage_stats['api_costs_saved'] += 1  # Estimate 1 cost unit per request
                    logger.debug(f"Deduplicated request: {endpoint}")
                    return True
            
            # Add to cache
            self.deduplication_cache[request_hash] = current_time
            return False
    
    def check_rate_limit(self, api_type: str = 'default') -> bool:
        """
        Check if a request would exceed rate limits
        
        Args:
            api_type: Type of API (default, research, financial)
            
        Returns:
            True if allowed, False if rate limited
        """
        current_time = time.time()
        limits = self.rate_limits.get(api_type, self.rate_limits['default'])
        
        with self.lock:
            # Clean old requests from history
            window_start = current_time - limits['time_window']
            self.request_history[api_type] = deque(
                req_time for req_time in self.request_history[api_type] 
                if req_time > window_start
            )
            
            # Check if we're at the limit
            if len(self.request_history[api_type]) >= limits['max_requests']:
                self.usage_stats['rate_limited_requests'] += 1
                logger.warning(f"Rate limit exceeded for {api_type} API")
                return False
            
            # Add current request to history
            self.request_history[api_type].append(current_time)
            self.usage_stats['total_requests'] += 1
            return True
    
    def batch_requests(self, api_type: str, request_data: Dict) -> Optional[List[Dict]]:
        """
        Add request to batch queue and return batch if ready
        
        Args:
            api_type: Type of API
            request_data: Request data to batch
            
        Returns:
            Batch of requests if ready, None if waiting for more
        """
        with self.lock:
            self.batch_queues[api_type].append(request_data)
            
            # Batch size thresholds
            batch_sizes = {
                'research': 3,  # Batch 3 research requests
                'financial': 2,  # Batch 2 financial requests
                'default': 5,   # Batch 5 default requests
            }
            
            batch_size = batch_sizes.get(api_type, 3)
            
            if len(self.batch_queues[api_type]) >= batch_size:
                batch = self.batch_queues[api_type][:batch_size]
                self.batch_queues[api_type] = self.batch_queues[api_type][batch_size:]
                self.usage_stats['batched_requests'] += len(batch)
                self.usage_stats['api_costs_saved'] += len(batch) - 1  # Save n-1 API calls
                logger.debug(f"Created batch of {len(batch)} requests for {api_type} API")
                return batch
        
        return None
    
    def wait_for_rate_limit(self, api_type: str = 'default', max_wait: int = 30) -> bool:
        """
        Wait until rate limit allows another request
        
        Args:
            api_type: Type of API
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if allowed, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.check_rate_limit(api_type):
                return True
            time.sleep(1)  # Wait 1 second between checks
        
        logger.warning(f"Timeout waiting for rate limit reset for {api_type} API")
        return False
    
    def optimize_search_queries(self, queries: List[str]) -> List[str]:
        """
        Optimize search queries to reduce redundant API calls
        
        Args:
            queries: List of search queries
            
        Returns:
            Optimized list of unique queries
        """
        if not queries:
            return []
        
        # Simple deduplication based on normalized query strings
        # Removed keyword-based heuristics to avoid arbitrary filtering
        unique_queries = []
        seen_queries = set()
        
        for query in queries:
            normalized_query = query.strip().lower()
            if normalized_query not in seen_queries:
                unique_queries.append(query)
                seen_queries.add(normalized_query)
        
        logger.info(f"Optimized {len(queries)} queries to {len(unique_queries)} unique queries")
        return unique_queries
    
    def estimate_cost_savings(self) -> Dict[str, Any]:
        """Estimate cost savings from optimization"""
        total_savings = self.usage_stats['api_costs_saved']
        
        # Estimate monetary savings (assuming $0.01 per API call)
        monetary_savings = total_savings * 0.01
        
        return {
            'total_requests': self.usage_stats['total_requests'],
            'batched_requests': self.usage_stats['batched_requests'],
            'deduplicated_requests': self.usage_stats['deduplicated_requests'],
            'rate_limited_requests': self.usage_stats['rate_limited_requests'],
            'estimated_api_calls_saved': total_savings,
            'estimated_monetary_savings': round(monetary_savings, 2),
            'optimization_efficiency': round(
                (total_savings / max(1, self.usage_stats['total_requests'])) * 100, 2
            )
        }
    
    def get_usage_metrics(self) -> Dict[str, Any]:
        """Get current usage metrics"""
        current_time = time.time()
        metrics = {}
        
        for api_type, limits in self.rate_limits.items():
            window_start = current_time - limits['time_window']
            recent_requests = [
                req_time for req_time in self.request_history[api_type]
                if req_time > window_start
            ]
            
            metrics[api_type] = {
                'recent_requests': len(recent_requests),
                'rate_limit': limits['max_requests'],
                'time_window': limits['time_window'],
                'remaining_requests': max(0, limits['max_requests'] - len(recent_requests))
            }
        
        return metrics
    
    def reset_usage_stats(self):
        """Reset usage statistics"""
        with self.lock:
            self.usage_stats = {
                'total_requests': 0,
                'batched_requests': 0,
                'deduplicated_requests': 0,
                'rate_limited_requests': 0,
                'api_costs_saved': 0
            }
            self.request_history.clear()
            self.deduplication_cache.clear()
            self.batch_queues.clear()


# Global API optimizer instance
api_optimizer = APIOptimizer()


def optimize_api_call(api_type: str = 'default', deduplicate: bool = True):
    """
    Decorator to optimize API calls with rate limiting and deduplication
    
    Args:
        api_type: Type of API
        deduplicate: Whether to check for duplicates
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract endpoint and parameters for deduplication
            endpoint = func.__name__
            params = kwargs.copy()
            
            # Check for duplicates
            if deduplicate and api_optimizer.check_duplicate(endpoint, params):
                return {'success': False, 'error': 'Duplicate request skipped'}
            
            # Wait for rate limit if needed
            if not api_optimizer.check_rate_limit(api_type):
                if not api_optimizer.wait_for_rate_limit(api_type):
                    return {
                        'success': False, 
                        'error': 'Rate limit exceeded, please try again later'
                    }
            
            # Execute the API call
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def batch_api_calls(api_type: str):
    """
    Decorator to batch API calls
    
    Args:
        api_type: Type of API for batching
    """
    def decorator(func):
        def wrapper(request_data):
            batch = api_optimizer.batch_requests(api_type, request_data)
            if batch:
                return func(batch)
            return {'success': True, 'status': 'queued_for_batch'}
        return wrapper
