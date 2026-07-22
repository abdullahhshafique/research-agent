from django.test import TestCase
from apps.utils.validators import validate_query, sanitize_input


class ValidatorTests(TestCase):
    def test_valid_query(self):
        is_valid, error = validate_query("AI agents 2026", 500)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_empty_query(self):
        is_valid, error = validate_query("", 500)
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())
    
    def test_query_too_long(self):
        is_valid, error = validate_query("a" * 501, 500)
        self.assertFalse(is_valid)
        self.assertIn("too long", error.lower())
    
    def test_sanitize_input(self):
        result = sanitize_input("<script>alert('xss')</script>hello")
        self.assertNotIn("<script>", result)
        self.assertIn("hello", result)
    
    def test_extract_domain(self):
        from apps.utils.validators import extract_domain
        result = extract_domain("https://example.com/path")
        self.assertEqual(result, "example.com")


class HTTPClientTests(TestCase):
    def test_client_init(self):
        from apps.utils.http_client import HTTPClient
        client = HTTPClient(base_url="https://api.example.com")
        self.assertEqual(client.base_url, "https://api.example.com")
        self.assertEqual(client.timeout, 30)
    
    def test_circuit_breaker(self):
        from apps.utils.http_client import HTTPClient, CircuitBreakerOpen
        client = HTTPClient()
        client._circuit_open = True
        client._circuit_reset_time = __import__('time').time() + 1000
        
        with self.assertRaises(CircuitBreakerOpen):
            client._check_circuit()