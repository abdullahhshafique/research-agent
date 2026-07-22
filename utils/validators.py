"""
Input validation utilities.
"""
import re


# Use word boundaries to avoid false positives like "backpack" containing "hack"
BLOCKED_WORDS = [r'\bspam\b', r'\bscam\b', r'\bhack\b', r'\bcrack\b']


def validate_query(text: str, max_length: int = 500) -> tuple:
    """
    Validate research query.
    
    Returns:
        (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Query cannot be empty."
    
    if len(text) > max_length:
        return False, f"Query too long. Maximum {max_length} characters."
    
    # Profanity filter with word boundaries to avoid false positives
    lower_text = text.lower()
    for pattern in BLOCKED_WORDS:
        if re.search(pattern, lower_text):
            return False, "Query contains prohibited content."
    
    return True, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove excessive whitespace
    text = ' '.join(text.split())
    return text


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    """
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except Exception:
        return url