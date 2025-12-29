"""Cache Manager for I2POC Application"""

import json
import hashlib
import time
import os
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for research results to improve performance"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_ttl = {
            'company_research': 7 * 24 * 60 * 60,  # 7 days
            'idea_research': 3 * 24 * 60 * 60,     # 3 days
            'roi_analysis': 7 * 24 * 60 * 60,      # 7 days
            'question_generation': 1 * 24 * 60 * 60,  # 1 day
        }
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0,
            'expired': 0
        }
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _generate_cache_key(self, cache_type: str, *args) -> str:
        """Generate a unique cache key based on input parameters"""
        key_string = f"{cache_type}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get the file path for a cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, cache_type: str, *args) -> Optional[Dict[str, Any]]:
        """
        Get cached data if it exists and is not expired
        
        Args:
            cache_type: Type of cache (company_research, idea_research, etc.)
            *args: Arguments used to generate cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._generate_cache_key(cache_type, *args)
        cache_file = self._get_cache_file_path(cache_key)
        
        if not os.path.exists(cache_file):
            self.cache_stats['misses'] += 1
            logger.debug(f"Cache miss for {cache_type}: {args}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cache_time = cache_data.get('timestamp', 0)
            current_time = time.time()
            ttl = self.cache_ttl.get(cache_type, 24 * 60 * 60)  # Default 1 day
            
            if current_time - cache_time > ttl:
                self.cache_stats['expired'] += 1
                logger.debug(f"Cache expired for {cache_type}: {args}")
                os.remove(cache_file)  # Clean up expired cache
                return None
            
            self.cache_stats['hits'] += 1
            logger.debug(f"Cache hit for {cache_type}: {args}")
            return cache_data.get('data')
            
        except (json.JSONDecodeError, KeyError, IOError) as e:
            logger.warning(f"Error reading cache file {cache_file}: {str(e)}")
            self.cache_stats['misses'] += 1
            return None
    
    def set(self, cache_type: str, data: Dict[str, Any], *args) -> bool:
        """
        Store data in cache
        
        Args:
            cache_type: Type of cache (company_research, idea_research, etc.)
            data: Data to cache
            *args: Arguments used to generate cache key
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_cache_key(cache_type, *args)
        cache_file = self._get_cache_file_path(cache_key)
        
        cache_data = {
            'timestamp': time.time(),
            'cache_type': cache_type,
            'args': args,
            'data': data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.cache_stats['writes'] += 1
            logger.debug(f"Cache set for {cache_type}: {args}")
            return True
            
        except IOError as e:
            logger.error(f"Error writing cache file {cache_file}: {str(e)}")
            return False
    
    def invalidate(self, cache_type: str, *args) -> bool:
        """
        Remove specific cache entry
        
        Args:
            cache_type: Type of cache
            *args: Arguments used to generate cache key
            
        Returns:
            True if removed, False if not found
        """
        cache_key = self._generate_cache_key(cache_type, *args)
        cache_file = self._get_cache_file_path(cache_key)
        
        if os.path.exists(cache_file):
            os.remove(cache_file)
            logger.debug(f"Cache invalidated for {cache_type}: {args}")
            return True
        
        return False
    
    def invalidate_type(self, cache_type: str) -> int:
        """
        Remove all cache entries of a specific type
        
        Args:
            cache_type: Type of cache to invalidate
            
        Returns:
            Number of cache entries removed
        """
        removed_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if cache_data.get('cache_type') == cache_type:
                        os.remove(filepath)
                        removed_count += 1
                        
                except (json.JSONDecodeError, KeyError, IOError):
                    continue
        
        logger.debug(f"Invalidated {removed_count} cache entries for {cache_type}")
        return removed_count
    
    def clear_all(self) -> int:
        """
        Clear all cache entries
        
        Returns:
            Number of cache entries removed
        """
        removed_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                os.remove(filepath)
                removed_count += 1
        
        logger.debug(f"Cleared all {removed_count} cache entries")
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_operations = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'writes': self.cache_stats['writes'],
            'expired': self.cache_stats['expired'],
            'hit_rate': round(hit_rate, 2),
            'total_operations': total_operations,
            'cache_size': len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])
        }
    
    def cleanup_expired(self) -> int:
        """Clean up all expired cache entries"""
        removed_count = 0
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cache_type = cache_data.get('cache_type')
                    cache_time = cache_data.get('timestamp', 0)
                    ttl = self.cache_ttl.get(cache_type, 24 * 60 * 60)
                    
                    if current_time - cache_time > ttl:
                        os.remove(filepath)
                        removed_count += 1
                        self.cache_stats['expired'] += 1
                        
                except (json.JSONDecodeError, KeyError, IOError):
                    continue
        
        logger.debug(f"Cleaned up {removed_count} expired cache entries")
        return removed_count


# Global cache manager instance
cache_manager = CacheManager()
