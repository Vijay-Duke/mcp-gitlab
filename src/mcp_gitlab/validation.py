"""Validation utilities for tool arguments."""

import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from mcp import types

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Callable[..., Any])


def validate_tool_args(
    required_args: Optional[Dict[str, type]] = None,
    optional_args: Optional[Dict[str, type]] = None,
) -> Callable[[T], T]:
    """
    Decorator to validate tool arguments at runtime.
    
    Args:
        required_args: Dict mapping required argument names to their expected types
        optional_args: Dict mapping optional argument names to their expected types
    
    Returns:
        Decorated function that validates arguments before execution
    """
    required_args = required_args or {}
    optional_args = optional_args or {}
    
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(request: types.CallToolRequest) -> types.CallToolResult:
            arguments = request.params.arguments or {}
            
            # Validate required arguments
            for arg_name, expected_type in required_args.items():
                if arg_name not in arguments:
                    return types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=f"Missing required argument: {arg_name}"
                            )
                        ]
                    )
                
                value = arguments[arg_name]
                if not isinstance(value, expected_type):
                    return types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=f"Invalid type for argument '{arg_name}': expected {expected_type.__name__}, got {type(value).__name__}"
                            )
                        ]
                    )
            
            # Validate optional arguments if present
            for arg_name, expected_type in optional_args.items():
                if arg_name in arguments:
                    value = arguments[arg_name]
                    if not isinstance(value, expected_type):
                        return types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text=f"Invalid type for argument '{arg_name}': expected {expected_type.__name__}, got {type(value).__name__}"
                                )
                            ]
                        )
            
            # Validate no unexpected arguments
            all_valid_args = set(required_args.keys()) | set(optional_args.keys())
            unexpected_args = set(arguments.keys()) - all_valid_args
            if unexpected_args:
                return types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"Unexpected arguments: {', '.join(unexpected_args)}"
                        )
                    ]
                )
            
            # All validation passed, call the original function
            return await func(request)
        
        return wrapper
    
    return decorator


def validate_gitlab_id(value: Union[str, int]) -> bool:
    """Validate GitLab project/user/group ID."""
    if isinstance(value, int):
        return value > 0
    if isinstance(value, str):
        return value.strip() != "" and (value.isdigit() or "/" in value)
    return False


def validate_pagination_params(arguments: Dict[str, Any]) -> Optional[str]:
    """
    Validate pagination parameters.
    
    Returns:
        Error message if validation fails, None if validation passes
    """
    page = arguments.get('page')
    per_page = arguments.get('per_page')
    
    if page is not None:
        if not isinstance(page, int) or page < 1:
            return "Page must be a positive integer"
    
    if per_page is not None:
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            return "Per page must be an integer between 1 and 100"
    
    return None