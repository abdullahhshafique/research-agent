import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from django.conf import settings
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SearchCache:
    """
    File-based cache for Tavily search results.
    Cache expires after 1 hour by default.
    """
    
    def __init__(self, cache_dir: str = None, ttl_minutes: int = 60):
        self.cache_dir = cache_dir or os.path.join(settings.BASE_DIR, 'cache', 'search')
        self.ttl = timedelta(minutes=ttl_minutes)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, query: str, search_depth: str, max_results: int) -> str:
        """Generate cache key from search parameters."""
        key_string = f"{query.strip().lower()}|{search_depth}|{max_results}"
        return hashlib.md5(key_string.encode()).hexdigest() + '.json'
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get full path to cache file."""
        return os.path.join(self.cache_dir, cache_key)
    
    def get(self, query: str, search_depth: str, max_results: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached search results if not expired.
        
        Returns:
            Cached results dict or None if miss/expired
        """
        cache_key = self._get_cache_key(query, search_depth, max_results)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            if datetime.now() - cached_time > self.ttl:
                logger.info(f"Cache expired for query: {query[:50]}...")
                os.remove(cache_path)
                return None
            
            logger.info(f"Cache hit for query: {query[:50]}...")
            return cached_data['results']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Cache read error: {e}")
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, query: str, search_depth: str, max_results: int, results: Dict[str, Any]) -> None:
        """Store search results in cache."""
        cache_key = self._get_cache_key(query, search_depth, max_results)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'query': query,
            'search_depth': search_depth,
            'max_results': max_results,
            'results': results
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
            logger.info(f"Cached results for query: {query[:50]}...")
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    def clear(self, query: str = None, force: bool = False) -> int:
        """
        Clear cache entries. If query provided, clears specific entry.
        If force=True, clears ALL entries regardless of expiration.
        Otherwise clears only expired entries.
        
        Returns:
            Number of entries cleared
        """
        cleared = 0
        
        if query:
            # Clear specific query
            for depth in ['basic', 'advanced']:
                for max_res in [3, 5, 7, 10]:
                    cache_key = self._get_cache_key(query, depth, max_res)
                    cache_path = self._get_cache_path(cache_key)
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                        cleared += 1
        elif force:
            # Clear ALL entries
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    try:
                        os.remove(cache_path)
                        cleared += 1
                    except Exception:
                        pass
        else:
            # Clear all expired entries
            now = datetime.now()
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                cache_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    cached_time = datetime.fromisoformat(data['cached_at'])
                    if now - cached_time > self.ttl:
                        os.remove(cache_path)
                        cleared += 1
                except Exception:
                    os.remove(cache_path)
                    cleared += 1
        
        logger.info(f"Cleared {cleared} cache entries")
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_files = 0
        total_size = 0
        expired_count = 0
        now = datetime.now()
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            cache_path = os.path.join(self.cache_dir, filename)
            total_files += 1
            total_size += os.path.getsize(cache_path)
            
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                cached_time = datetime.fromisoformat(data['cached_at'])
                if now - cached_time > self.ttl:
                    expired_count += 1
            except Exception:
                expired_count += 1
        
        return {
            'total_entries': total_files,
            'expired_entries': expired_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.cache_dir
        }