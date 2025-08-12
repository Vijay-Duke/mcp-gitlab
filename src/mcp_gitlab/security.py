"""
Security utilities and constants for MCP GitLab server.
"""

import hashlib
import secrets
import string
from typing import Optional


# Security headers for API requests
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'none'",
}


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Length of the token
        
    Returns:
        Secure random token
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_token(token: str, salt: Optional[str] = None) -> str:
    """
    Hash a token using SHA-256 with optional salt.
    
    Args:
        token: Token to hash
        salt: Optional salt for hashing
        
    Returns:
        Hashed token
    """
    if salt:
        token = f"{salt}{token}"
    return hashlib.sha256(token.encode()).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal
    """
    return secrets.compare_digest(a.encode(), b.encode())


def sanitize_log_message(message: str) -> str:
    """
    Sanitize message for logging to prevent log injection.
    
    Args:
        message: Message to sanitize
        
    Returns:
        Sanitized message
    """
    # Remove newlines and control characters
    sanitized = message.replace('\n', ' ').replace('\r', ' ')
    
    # Remove other control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char == '\t')
    
    # Truncate if too long
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...'
    
    return sanitized


def is_safe_redirect_url(url: str, allowed_hosts: list) -> bool:
    """
    Check if URL is safe for redirect.
    
    Args:
        url: URL to check
        allowed_hosts: List of allowed hosts
        
    Returns:
        True if URL is safe
    """
    from urllib.parse import urlparse
    
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        
        # Only allow HTTPS (or HTTP for localhost)
        if parsed.scheme not in ['https', 'http']:
            return False
        
        if parsed.scheme == 'http' and parsed.hostname not in ['localhost', '127.0.0.1', '::1']:
            return False
        
        # Check if host is allowed
        if parsed.hostname not in allowed_hosts:
            return False
        
        return True
        
    except Exception:
        return False


class SecurityContext:
    """
    Security context for request handling.
    """
    
    def __init__(self, client_id: str, request_id: Optional[str] = None):
        """
        Initialize security context.
        
        Args:
            client_id: Client identifier
            request_id: Optional request ID for tracking
        """
        self.client_id = client_id
        self.request_id = request_id or generate_secure_token(16)
        self.start_time = None
        self.rate_limit_remaining = None
    
    def log_security_event(self, event_type: str, details: dict):
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Sanitize details
        sanitized_details = {
            k: sanitize_log_message(str(v)) if isinstance(v, str) else v
            for k, v in details.items()
        }
        
        logger.info(
            f"Security event: {event_type} | "
            f"Client: {self.client_id} | "
            f"Request: {self.request_id} | "
            f"Details: {sanitized_details}"
        )