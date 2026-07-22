"""
Custom HTTP client using only Python standard library.
Implements retry logic, timeouts, and circuit breaker pattern.
"""
import json
import urllib.request
import urllib.error
import urllib.parse
import socket
import time
import logging
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass


class AuthError(APIError):
    """Authentication error (401/403)."""
    pass


class CircuitBreakerOpen(APIError):
    """Circuit breaker is open."""
    pass


class HTTPClient:
    """
    Standard library HTTP client with retry and circuit breaker.
    
    Args:
        base_url: Base URL for all requests
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        retry_delay: Initial delay between retries (exponential backoff)
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._failure_count = 0
        self._circuit_open = False
        self._circuit_reset_time = 0
        self._circuit_threshold = 5  # Failures before opening
        self._circuit_timeout = 60   # Seconds before half-open
    
    def _check_circuit(self) -> None:
        """Check if circuit breaker allows requests."""
        if self._circuit_open:
            if time.time() - self._circuit_reset_time > self._circuit_timeout:
                logger.info("Circuit breaker entering half-open state")
                self._circuit_open = False
                self._failure_count = 0
            else:
                raise CircuitBreakerOpen("Circuit breaker is open. Service temporarily unavailable.")
    
    def _record_failure(self) -> None:
        """Record a failure and potentially open circuit."""
        self._failure_count += 1
        if self._failure_count >= self._circuit_threshold:
            logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
            self._circuit_open = True
            self._circuit_reset_time = time.time()
    
    def _record_success(self) -> None:
        """Record a successful request."""
        if self._failure_count > 0:
            self._failure_count = 0
            logger.info("Circuit breaker reset after successful request")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Returns:
            Parsed JSON response
        """
        self._check_circuit()
        
        # Build URL
        url = f"{self.base_url}{endpoint}"
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        
        # Build request
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AI-Research-Agent/1.0'
        }
        if headers:
            request_headers.update(headers)
        
        # Encode data
        body = None
        if data is not None:
            body = json.dumps(data).encode('utf-8')
        
        # Retry loop
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers=request_headers,
                    method=method
                )
                
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    self._record_success()
                    response_body = response.read().decode('utf-8')
                    
                    if response.status == 204:
                        return {}
                    
                    return json.loads(response_body)
                    
            except urllib.error.HTTPError as e:
                last_exception = e
                # FIX: Read response body once and store it
                error_body = None
                try:
                    error_bytes = e.read()
                    if error_bytes:
                        error_body = error_bytes.decode('utf-8')
                except Exception:
                    pass
                
                if e.code == 429:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        status_code=e.code,
                        response_body=error_body
                    )
                
                # Handle auth errors distinctly - don't retry 401/403
                if e.code in (401, 403):
                    raise AuthError(
                        f"Authentication failed (HTTP {e.code}): {error_body}",
                        status_code=e.code,
                        response_body=error_body
                    )
                
                if e.code >= 500:
                    # Server error, retry
                    self._record_failure()
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Server error {e.code}, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    # Client error (400, 404, etc.), don't retry
                    raise APIError(
                        f"HTTP {e.code}: {error_body}",
                        status_code=e.code,
                        response_body=error_body
                    )
                    
            except (urllib.error.URLError, socket.timeout) as e:
                last_exception = e
                self._record_failure()
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Connection error, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(wait_time)
                continue
            
            except json.JSONDecodeError as e:
                raise APIError(f"Invalid JSON response: {e}")
        
        # All retries exhausted
        raise APIError(f"Request failed after {self.max_retries} attempts: {last_exception}")
    
    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request('GET', endpoint, headers=headers, params=params)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request('POST', endpoint, data=data, headers=headers)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request('PUT', endpoint, data=data, headers=headers)
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request('DELETE', endpoint, headers=headers)