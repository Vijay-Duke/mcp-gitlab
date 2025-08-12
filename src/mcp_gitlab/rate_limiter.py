"""
Rate limiting utilities for MCP GitLab server.
Helps prevent API abuse and ensures fair usage.
"""

import time
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from threading import Lock
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    cooldown_seconds: int = 60


class RateLimiter:
    """
    Token bucket rate limiter implementation.
    Provides per-client rate limiting based on client ID.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = Lock()
        self._request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
    
    def check_rate_limit(self, client_id: str) -> Tuple[bool, Optional[float]]:
        """
        Check if request is allowed under rate limits.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Tuple of (allowed, wait_time_seconds)
            If allowed is False, wait_time_seconds indicates how long to wait
        """
        with self._lock:
            # Get or create token bucket for client
            if client_id not in self._buckets:
                self._buckets[client_id] = TokenBucket(
                    capacity=self.config.burst_size,
                    refill_rate=self.config.requests_per_minute / 60.0
                )
            
            bucket = self._buckets[client_id]
            
            # Check minute rate limit
            if not bucket.consume():
                wait_time = bucket.time_until_token()
                logger.warning(f"Rate limit exceeded for client {client_id}, wait {wait_time:.1f}s")
                return False, wait_time
            
            # Check hour rate limit
            now = time.time()
            history = self._request_history[client_id]
            
            # Clean old entries
            while history and history[0] < now - 3600:
                history.popleft()
            
            if len(history) >= self.config.requests_per_hour:
                oldest = history[0]
                wait_time = 3600 - (now - oldest)
                logger.warning(f"Hourly rate limit exceeded for {client_id}, wait {wait_time:.1f}s")
                return False, wait_time
            
            # Record request
            history.append(now)
            
            return True, None
    
    def get_remaining_quota(self, client_id: str) -> Dict[str, int]:
        """
        Get remaining rate limit quota for a client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Dictionary with remaining quotas
        """
        with self._lock:
            history = self._request_history[client_id]
            now = time.time()
            
            # Count requests in last minute
            minute_ago = now - 60
            minute_count = sum(1 for t in history if t > minute_ago)
            
            # Count requests in last hour
            hour_count = len(history)
            
            return {
                'requests_per_minute_remaining': max(0, self.config.requests_per_minute - minute_count),
                'requests_per_hour_remaining': max(0, self.config.requests_per_hour - hour_count),
                'burst_remaining': self._buckets.get(client_id, TokenBucket()).tokens if client_id in self._buckets else self.config.burst_size
            }
    
    def reset_client(self, client_id: str):
        """
        Reset rate limits for a specific client.
        
        Args:
            client_id: Client to reset
        """
        with self._lock:
            if client_id in self._buckets:
                del self._buckets[client_id]
            if client_id in self._request_history:
                del self._request_history[client_id]
            logger.info(f"Reset rate limits for client {client_id}")


class TokenBucket:
    """
    Token bucket implementation for rate limiting.
    """
    
    def __init__(self, capacity: int = 10, refill_rate: float = 1.0):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def time_until_token(self) -> float:
        """
        Calculate time until next token is available.
        
        Returns:
            Seconds until next token
        """
        if self.tokens >= 1:
            return 0.0
        
        return (1 - self.tokens) / self.refill_rate
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now


class GitLabAPIRateLimiter:
    """
    GitLab API specific rate limiter.
    Respects GitLab's rate limits and headers.
    """
    
    def __init__(self):
        """Initialize GitLab API rate limiter."""
        self._limits: Dict[str, Dict] = {}
        self._lock = Lock()
    
    def update_from_headers(self, client_id: str, headers: Dict[str, str]):
        """
        Update rate limit info from GitLab API headers.
        
        Args:
            client_id: Client identifier
            headers: Response headers from GitLab API
        """
        with self._lock:
            self._limits[client_id] = {
                'limit': int(headers.get('RateLimit-Limit', 0)),
                'remaining': int(headers.get('RateLimit-Remaining', 0)),
                'reset': int(headers.get('RateLimit-Reset', 0)),
                'observed_at': time.time()
            }
    
    def check_gitlab_limits(self, client_id: str) -> Tuple[bool, Optional[float]]:
        """
        Check GitLab API rate limits.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Tuple of (allowed, wait_time_seconds)
        """
        with self._lock:
            if client_id not in self._limits:
                return True, None
            
            limits = self._limits[client_id]
            
            # Check if we have remaining requests
            if limits['remaining'] > 0:
                return True, None
            
            # Calculate wait time
            now = time.time()
            reset_time = limits['reset']
            
            if reset_time > now:
                wait_time = reset_time - now
                logger.warning(f"GitLab API rate limit reached for {client_id}, wait {wait_time:.1f}s")
                return False, wait_time
            
            # Reset time has passed
            return True, None
    
    def get_gitlab_limits(self, client_id: str) -> Optional[Dict]:
        """
        Get current GitLab API limits for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dictionary with limit info or None
        """
        with self._lock:
            return self._limits.get(client_id)


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None
_gitlab_limiter: Optional[GitLabAPIRateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_gitlab_limiter() -> GitLabAPIRateLimiter:
    """Get or create global GitLab API rate limiter."""
    global _gitlab_limiter
    if _gitlab_limiter is None:
        _gitlab_limiter = GitLabAPIRateLimiter()
    return _gitlab_limiter


def check_rate_limits(client_id: str) -> Tuple[bool, Optional[float]]:
    """
    Check both internal and GitLab API rate limits.
    
    Args:
        client_id: Client identifier
        
    Returns:
        Tuple of (allowed, wait_time_seconds)
    """
    # Check internal rate limits
    internal_limiter = get_rate_limiter()
    allowed, wait_time = internal_limiter.check_rate_limit(client_id)
    
    if not allowed:
        return False, wait_time
    
    # Check GitLab API limits
    gitlab_limiter = get_gitlab_limiter()
    allowed, wait_time = gitlab_limiter.check_gitlab_limits(client_id)
    
    return allowed, wait_time