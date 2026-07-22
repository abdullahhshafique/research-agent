"""
Tavily search agent using standard library HTTP client.
"""
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from apps.utils.http_client import HTTPClient, APIError
from apps.utils.search_cache import SearchCache

logger = logging.getLogger(__name__)


class SearchResult:
    """Normalized search result."""
    
    def __init__(
        self,
        url: str,
        title: str,
        content: str,
        score: float,
        domain: str
    ):
        self.url = url
        self.title = title
        self.content = content
        self.score = score
        self.domain = domain
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'score': self.score,
            'domain': self.domain
        }
    
    def __repr__(self) -> str:
        return f"SearchResult(title='{self.title[:50]}...', score={self.score})"


class SearchAgent:
    """
    Tavily search agent for web research.
    Uses file-based caching to avoid redundant API calls.
    """
    
    BASE_URL = "https://api.tavily.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        if not self.api_key:
            raise ValueError("Tavily API key is required. Set TAVILY_API_KEY in environment.")
        
        self.client = HTTPClient(base_url=self.BASE_URL, timeout=30, max_retries=3)
        self.cache = SearchCache()
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_answer: bool = True,
        use_cache: bool = True
    ) -> List[SearchResult]:
        """
        Execute web search with caching.
        
        Args:
            query: Search query string
            max_results: Number of results (3-10)
            search_depth: 'basic' or 'advanced'
            include_answer: Include AI-generated answer
            use_cache: Whether to use cache (default True)
            
        Returns:
            List of SearchResult objects
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        max_results = max(3, min(10, max_results))
        
        if search_depth not in ('basic', 'advanced'):
            search_depth = 'advanced'
        
        # Try cache first
        if use_cache:
            cached_results = self.cache.get(query, search_depth, max_results)
            if cached_results:
                logger.info(f"Returning cached results for: {query[:50]}...")
                return [SearchResult(**item) for item in cached_results]
        
        logger.info(f"Searching Tavily: '{query[:50]}...' (depth={search_depth}, max={max_results})")
        
        # Use Authorization header instead of body parameter
        # Tavily API requires Bearer token in Authorization header
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": include_answer,
            "include_raw_content": True,
        }
        
        try:
            response = self.client.post("/search", data=payload, headers=headers)
            
            # Parse results
            results = []
            raw_results = response.get('results', [])
            
            for item in raw_results:
                result = SearchResult(
                    url=item.get('url', ''),
                    title=item.get('title', 'Untitled'),
                    content=item.get('content', item.get('raw_content', '')),
                    score=item.get('score', 0.0),
                    domain=self._extract_domain(item.get('url', ''))
                )
                results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Cache the results
            if use_cache:
                self.cache.set(query, search_depth, max_results, [r.to_dict() for r in results])
            
            logger.info(f"Search complete: {len(results)} results found")
            return results
            
        except APIError as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except Exception:
            return url
    
    def validate_sources(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Filter and validate search results.
        """
        validated = []
        suspicious_domains = {'bit.ly', 't.co', 'short.link'}
        
        for result in results:
            if not result.url or not result.url.startswith('http'):
                continue
            if result.score < 0.3:
                continue
            if result.domain in suspicious_domains:
                continue
            validated.append(result)
        
        return validated
    
    def clear_cache(self, query: str = None) -> int:
        """Clear search cache."""
        return self.cache.clear(query)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()