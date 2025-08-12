"""
Input validation utilities for MCP GitLab server.
Provides security-focused validation for user inputs.
"""

import re
from typing import Any, Optional, List
from urllib.parse import urlparse

# Maximum lengths to prevent abuse
MAX_PROJECT_PATH_LENGTH = 255
MAX_BRANCH_NAME_LENGTH = 255
MAX_FILE_PATH_LENGTH = 1024
MAX_COMMIT_MESSAGE_LENGTH = 50000
MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10MB
MAX_SEARCH_QUERY_LENGTH = 1000
MAX_COMMENT_LENGTH = 50000

# Regex patterns for validation
PROJECT_PATH_PATTERN = re.compile(r'^[\w\-\.]+/[\w\-\.]+$')
BRANCH_NAME_PATTERN = re.compile(r'^[\w\-\./]+$')
SHA_PATTERN = re.compile(r'^[a-fA-F0-9]{40}$')
REF_PATTERN = re.compile(r'^[\w\-\./]+$')


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


def validate_project_path(path: str) -> str:
    """
    Validate GitLab project path format.
    
    Args:
        path: Project path in format 'namespace/project'
        
    Returns:
        Validated project path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not path:
        raise ValidationError("Project path cannot be empty")
    
    if len(path) > MAX_PROJECT_PATH_LENGTH:
        raise ValidationError(f"Project path too long (max {MAX_PROJECT_PATH_LENGTH} chars)")
    
    # Remove any potential path traversal attempts
    if '..' in path or path.startswith('/') or path.startswith('~'):
        raise ValidationError("Invalid project path format")
    
    # Basic format validation
    if '/' not in path:
        raise ValidationError("Project path must be in format 'namespace/project'")
    
    return path.strip()


def validate_branch_name(branch: str) -> str:
    """
    Validate Git branch name.
    
    Args:
        branch: Branch name to validate
        
    Returns:
        Validated branch name
        
    Raises:
        ValidationError: If branch name is invalid
    """
    if not branch:
        raise ValidationError("Branch name cannot be empty")
    
    if len(branch) > MAX_BRANCH_NAME_LENGTH:
        raise ValidationError(f"Branch name too long (max {MAX_BRANCH_NAME_LENGTH} chars)")
    
    # Check for invalid characters
    if not BRANCH_NAME_PATTERN.match(branch):
        raise ValidationError("Branch name contains invalid characters")
    
    # Prevent path traversal
    if '..' in branch or branch.startswith('/'):
        raise ValidationError("Invalid branch name format")
    
    return branch.strip()


def validate_file_path(path: str) -> str:
    """
    Validate file path within repository.
    
    Args:
        path: File path to validate
        
    Returns:
        Validated file path
        
    Raises:
        ValidationError: If file path is invalid
    """
    if not path:
        raise ValidationError("File path cannot be empty")
    
    if len(path) > MAX_FILE_PATH_LENGTH:
        raise ValidationError(f"File path too long (max {MAX_FILE_PATH_LENGTH} chars)")
    
    # Prevent path traversal attacks
    if '..' in path or path.startswith('~'):
        raise ValidationError("Path traversal attempts are not allowed")
    
    # Remove leading slashes for consistency
    path = path.lstrip('/')
    
    # Check for null bytes (security issue)
    if '\x00' in path:
        raise ValidationError("File path contains invalid characters")
    
    return path


def validate_commit_message(message: str) -> str:
    """
    Validate commit message.
    
    Args:
        message: Commit message to validate
        
    Returns:
        Validated commit message
        
    Raises:
        ValidationError: If message is invalid
    """
    if not message:
        raise ValidationError("Commit message cannot be empty")
    
    if len(message) > MAX_COMMIT_MESSAGE_LENGTH:
        raise ValidationError(f"Commit message too long (max {MAX_COMMIT_MESSAGE_LENGTH} chars)")
    
    # Remove any potential control characters except newlines
    cleaned = ''.join(char for char in message if char == '\n' or not ord(char) < 32)
    
    return cleaned.strip()


def validate_content_size(content: str) -> str:
    """
    Validate content size to prevent abuse.
    
    Args:
        content: Content to validate
        
    Returns:
        Validated content
        
    Raises:
        ValidationError: If content is too large
    """
    if len(content) > MAX_CONTENT_SIZE:
        raise ValidationError(f"Content too large (max {MAX_CONTENT_SIZE} bytes)")
    
    return content


def validate_url(url: str) -> str:
    """
    Validate GitLab URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError("URL cannot be empty")
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            raise ValidationError("URL must include scheme (https://)")
        
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError("URL must use HTTP or HTTPS")
        
        if not parsed.netloc:
            raise ValidationError("URL must include domain")
        
        # Recommend HTTPS for security
        if parsed.scheme == 'http' and 'localhost' not in parsed.netloc:
            # Just a warning, not blocking
            pass
            
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}")
    
    return url.strip()


def validate_search_query(query: str) -> str:
    """
    Validate search query.
    
    Args:
        query: Search query to validate
        
    Returns:
        Validated query
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query:
        raise ValidationError("Search query cannot be empty")
    
    if len(query) > MAX_SEARCH_QUERY_LENGTH:
        raise ValidationError(f"Search query too long (max {MAX_SEARCH_QUERY_LENGTH} chars)")
    
    # Remove any potential SQL injection attempts (though GitLab API should handle this)
    dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute']
    query_lower = query.lower()
    for pattern in dangerous_patterns:
        if pattern in query_lower:
            # Just sanitize, don't block entirely
            query = query.replace(pattern, '')
    
    return query.strip()


def validate_ref(ref: str) -> str:
    """
    Validate Git ref (branch, tag, or commit SHA).
    
    Args:
        ref: Git ref to validate
        
    Returns:
        Validated ref
        
    Raises:
        ValidationError: If ref is invalid
    """
    if not ref:
        raise ValidationError("Git ref cannot be empty")
    
    # Check if it's a SHA
    if len(ref) == 40 and SHA_PATTERN.match(ref):
        return ref
    
    # Otherwise validate as branch/tag name
    if not REF_PATTERN.match(ref):
        raise ValidationError("Git ref contains invalid characters")
    
    # Prevent path traversal
    if '..' in ref:
        raise ValidationError("Invalid ref format")
    
    return ref.strip()


def validate_integer(value: Any, min_val: Optional[int] = None, 
                    max_val: Optional[int] = None, name: str = "value") -> int:
    """
    Validate integer input.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Parameter name for error messages
        
    Returns:
        Validated integer
        
    Raises:
        ValidationError: If value is invalid
    """
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be an integer")
    
    if min_val is not None and int_val < min_val:
        raise ValidationError(f"{name} must be at least {min_val}")
    
    if max_val is not None and int_val > max_val:
        raise ValidationError(f"{name} must be at most {max_val}")
    
    return int_val


def validate_list_input(items: Any, max_items: int = 100, 
                       item_validator: Optional[callable] = None) -> List:
    """
    Validate list input.
    
    Args:
        items: List to validate
        max_items: Maximum number of items allowed
        item_validator: Optional function to validate each item
        
    Returns:
        Validated list
        
    Raises:
        ValidationError: If list is invalid
    """
    if not isinstance(items, list):
        raise ValidationError("Input must be a list")
    
    if len(items) > max_items:
        raise ValidationError(f"Too many items (max {max_items})")
    
    if item_validator:
        validated_items = []
        for item in items:
            validated_items.append(item_validator(item))
        return validated_items
    
    return items


def sanitize_output(text: str, remove_tokens: bool = True) -> str:
    """
    Sanitize output to remove sensitive information.
    
    Args:
        text: Text to sanitize
        remove_tokens: Whether to remove token-like strings
        
    Returns:
        Sanitized text
    """
    if not text:
        return text
    
    if remove_tokens:
        # Remove GitLab tokens (they start with glpat-, gldt-, etc.)
        token_patterns = [
            r'glpat-[\w\-]+',  # Personal access token
            r'gldt-[\w\-]+',   # Deploy token
            r'glrt-[\w\-]+',   # Runner token
            r'gloa-[\w\-]+',   # OAuth token
            r'glimt-[\w\-]+',  # Impersonation token
            r'glcbt-[\w\-]+',  # Ci build token
        ]
        
        for pattern in token_patterns:
            text = re.sub(pattern, '[REDACTED]', text)
    
    # Remove potential passwords in URLs
    text = re.sub(r'(https?://)([^:]+):([^@]+)@', r'\1[REDACTED]:[REDACTED]@', text)
    
    return text