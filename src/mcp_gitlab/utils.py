"""
Utility functions for MCP GitLab server
"""
import time
import logging
from functools import lru_cache, wraps
from typing import Dict, Any, Callable, Optional
import gitlab.exceptions

from .constants import (
    ERROR_AUTH_FAILED,
    ERROR_NOT_FOUND,
    ERROR_RATE_LIMIT,
    ERROR_GENERIC,
    CACHE_MAX_SIZE,
    MAX_RETRIES,
    RETRY_DELAY_BASE,
    RETRY_BACKOFF_FACTOR,
    MAX_RETRY_DELAY
)

logger = logging.getLogger(__name__)


def sanitize_error(error: Exception, custom_message: Optional[str] = None) -> Dict[str, str]:
    """
    Sanitize error messages for user display.
    Logs full error details while returning user-friendly messages.
    
    Args:
        error: The exception that occurred
        custom_message: Optional custom message to use instead of default mapping
    """
    error_map = {
        gitlab.exceptions.GitlabAuthenticationError: ERROR_AUTH_FAILED,
        gitlab.exceptions.GitlabGetError: ERROR_NOT_FOUND,
        gitlab.exceptions.GitlabHttpError: ERROR_GENERIC,
        gitlab.exceptions.GitlabListError: ERROR_NOT_FOUND,
        gitlab.exceptions.GitlabCreateError: "Failed to create resource. Please check your input.",
        gitlab.exceptions.GitlabUpdateError: "Failed to update resource. Please check your input.",
        gitlab.exceptions.GitlabDeleteError: "Failed to delete resource. Please check permissions.",
    }
    
    # Use custom message if provided, otherwise use mapping or default
    if custom_message:
        message = custom_message
    elif hasattr(error, 'response_code') and error.response_code == 429:
        message = ERROR_RATE_LIMIT
    else:
        error_type = type(error)
        message = error_map.get(error_type, ERROR_GENERIC)
    
    # Log the full error details for debugging
    logger.error(f"Error occurred: {type(error).__name__}: {str(error)}")
    if hasattr(error, '__traceback__'):
        import traceback
        logger.debug(f"Traceback: {traceback.format_tb(error.__traceback__)}")
    
    return {
        "error": message,
        "type": type(error).__name__
    }


def timed_cache(seconds: int):
    """
    Decorator that provides time-based caching using lru_cache.
    Cache expires after the specified number of seconds.
    """
    def decorator(func: Callable) -> Callable:
        # Apply lru_cache
        func = lru_cache(maxsize=CACHE_MAX_SIZE)(func)
        func.lifetime = seconds
        func.expiration = time.time() + seconds
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if cache has expired
            if time.time() > func.expiration:
                func.cache_clear()
                func.expiration = time.time() + func.lifetime
            return func(*args, **kwargs)
        
        # Add method to manually clear cache
        wrapper.cache_clear = func.cache_clear
        wrapper.cache_info = func.cache_info
        
        return wrapper
    return decorator


def retry_on_error(
    max_retries: int = MAX_RETRIES,
    delay: float = RETRY_DELAY_BASE,
    backoff_factor: float = RETRY_BACKOFF_FACTOR,
    max_delay: float = MAX_RETRY_DELAY,
    retry_exceptions: tuple = (gitlab.exceptions.GitlabHttpError,)
):
    """
    Decorator that implements retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay between retries
        retry_exceptions: Tuple of exceptions that should trigger a retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _execute_with_retry(
                func, args, kwargs, max_retries, delay, 
                backoff_factor, max_delay, retry_exceptions
            )
        return wrapper
    return decorator


def _execute_with_retry(
    func: Callable,
    args: tuple,
    kwargs: dict,
    max_retries: int,
    delay: float,
    backoff_factor: float,
    max_delay: float,
    retry_exceptions: tuple
) -> Any:
    """
    Helper function to execute a function with retry logic.
    
    This is extracted to reduce cognitive complexity of the decorator.
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retry_exceptions as e:
            last_exception = e
            
            # Check if it's a rate limit error (don't retry those)
            if _is_rate_limit_error(e):
                raise
            
            if attempt < max_retries:
                _log_retry_attempt(func.__name__, attempt, max_retries, e, current_delay)
                time.sleep(current_delay)
                current_delay = min(current_delay * backoff_factor, max_delay)
            else:
                logger.error(f"All retry attempts failed for {func.__name__}")
    
    # If we get here, all retries failed
    if last_exception:
        raise last_exception


def _is_rate_limit_error(exception: Exception) -> bool:
    """Check if an exception is a rate limit error."""
    return hasattr(exception, 'response_code') and exception.response_code == 429


def _log_retry_attempt(
    func_name: str,
    attempt: int,
    max_retries: int,
    exception: Exception,
    delay: float
) -> None:
    """Log a retry attempt."""
    logger.warning(
        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func_name}: {str(exception)}. "
        f"Retrying in {delay:.1f} seconds..."
    )


def truncate_response(data: Any, max_size: int = 25000) -> Any:
    """
    Truncate response data to avoid token limit errors.
    
    Args:
        data: The data to potentially truncate
        max_size: Maximum size in characters
        
    Returns:
        Truncated data with a note if truncation occurred
    """
    import json
    
    # Convert to JSON string to check size
    json_str = json.dumps(data, indent=2)
    
    if len(json_str) <= max_size:
        return data
    
    # If it's a list, use the list truncation helper
    if isinstance(data, list):
        return _truncate_list_response(data, max_size)
    
    # For other types, return a truncation message
    return {
        "truncated": True,
        "message": "Response too large. Please use pagination or filters to reduce the response size.",
        "size": len(json_str)
    }


def _truncate_list_response(data: list, max_size: int) -> Dict[str, Any]:
    """
    Helper function to truncate list responses.
    
    Args:
        data: List to truncate
        max_size: Maximum size in characters
        
    Returns:
        Dictionary with truncated data and metadata
    """
    import json
    
    truncated_list = []
    current_size = 2  # For "[]"
    
    for item in data:
        item_str = json.dumps(item, indent=2)
        if current_size + len(item_str) + 1 > max_size:  # +1 for comma
            break
        truncated_list.append(item)
        current_size += len(item_str) + 1
    
    return {
        "data": truncated_list,
        "truncated": True,
        "original_count": len(data),
        "returned_count": len(truncated_list),
        "message": f"Response truncated to avoid token limits. Showing {len(truncated_list)} of {len(data)} items."
    }


def requires_project(func: Callable) -> Callable:
    """
    Decorator that handles project detection and validation.
    Automatically injects project_id if not provided in arguments.
    """
    @wraps(func)
    def wrapper(client, arguments: Optional[Dict[str, Any]] = None):
        from .constants import ERROR_NO_PROJECT
        
        # Get project_id and add it to arguments if needed
        project_id = _get_project_id_or_detect(client, arguments, ERROR_NO_PROJECT)
        
        # Ensure arguments dict exists and has project_id
        if arguments is None:
            arguments = {}
        arguments["project_id"] = project_id
        
        return func(client, arguments)
    
    return wrapper


def _get_project_id_or_detect(client: Any, arguments: Optional[Dict[str, Any]], error_message: str) -> str:
    """
    Helper function to get project ID from arguments or detect from git.
    
    Args:
        client: GitLab client instance
        arguments: Optional arguments dictionary
        error_message: Error message to raise if no project found
        
    Returns:
        Project ID string
        
    Raises:
        ValueError: If no project ID provided and detection fails
    """
    if arguments and arguments.get("project_id"):
        return arguments["project_id"]
    
    detected = client.get_project_from_git(".")
    if detected:
        return detected["id"]
    
    raise ValueError(error_message)


class GitLabClientManager:
    """
    Singleton manager for GitLab client instances.
    Ensures only one client is created and reused across tool calls.
    """
    _instance: Optional['GitLabClientManager'] = None
    _client: Optional[Any] = None
    _config_hash: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self, config: 'GitLabConfig') -> 'GitLabClient':
        """
        Get or create a GitLab client instance.
        Creates a new client if configuration has changed.
        """
        # Import here to avoid circular imports
        from .gitlab_client import GitLabClient
        
        # Generate a hash of the current configuration
        import hashlib
        config_str = f"{config.url}:{config.private_token or ''}:{config.oauth_token or ''}"
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()
        
        # Create new client if configuration changed or no client exists
        if self._client is None or self._config_hash != config_hash:
            logger.info("Creating new GitLab client instance")
            self._client = GitLabClient(config)
            self._config_hash = config_hash
        else:
            logger.debug("Reusing existing GitLab client instance")
        
        return self._client
    
    def clear_client(self):
        """Clear the cached client instance."""
        self._client = None
        self._config_hash = None
