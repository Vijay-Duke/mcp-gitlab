"""Decorator utilities to reduce boilerplate in tool handlers."""

import functools
import logging
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar

import gitlab
from mcp import types

from .gitlab_client import GitLabClient

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Callable[..., Awaitable[types.CallToolResult]])


def gitlab_tool(
    requires_auth: bool = True,
    paginated: bool = False,
    max_per_page: int = 100,
) -> Callable[[T], T]:
    """
    Decorator to handle common GitLab tool patterns.
    
    Args:
        requires_auth: Whether the tool requires GitLab authentication
        paginated: Whether the tool supports pagination
        max_per_page: Maximum items per page for paginated requests
    
    Returns:
        Decorated function with common error handling and client setup
    """
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(
            client: GitLabClient,
            request: types.CallToolRequest,
        ) -> types.CallToolResult:
            try:
                arguments = request.params.arguments or {}
                
                # Check authentication if required
                if requires_auth and not client.is_authenticated():
                    return types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="GitLab authentication required. Please configure your GitLab token."
                            )
                        ]
                    )
                
                # Handle pagination parameters if supported
                if paginated:
                    page = arguments.get('page', 1)
                    per_page = arguments.get('per_page', 20)
                    
                    if not isinstance(page, int) or page < 1:
                        return types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text="Page must be a positive integer"
                                )
                            ]
                        )
                    
                    if not isinstance(per_page, int) or per_page < 1 or per_page > max_per_page:
                        return types.CallToolResult(
                            content=[
                                types.TextContent(
                                    type="text",
                                    text=f"Per page must be an integer between 1 and {max_per_page}"
                                )
                            ]
                        )
                
                # Call the original function
                return await func(client, request)
                
            except gitlab.GitlabAuthenticationError:
                logger.error("GitLab authentication failed")
                return types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text="GitLab authentication failed. Please check your token and permissions."
                        )
                    ]
                )
            except gitlab.GitlabGetError as e:
                logger.error(f"GitLab API error: {e}")
                if e.response_code == 404:
                    return types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="Resource not found. Please check the ID or path provided."
                            )
                        ]
                    )
                elif e.response_code == 403:
                    return types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text="Access denied. You don't have permission to access this resource."
                            )
                        ]
                    )
                else:
                    return types.CallToolResult(
                        content=[
                            types.TextContent(
                                type="text",
                                text=f"GitLab API error: {str(e)}"
                            )
                        ]
                    )
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                return types.CallToolResult(
                    content=[
                        types.TextContent(
                            type="text",
                            text=f"An unexpected error occurred: {str(e)}"
                        )
                    ]
                )
        
        return wrapper
    
    return decorator


def format_response(
    data: Any,
    template: Optional[str] = None,
    max_length: int = 10000,
) -> types.CallToolResult:
    """
    Format response data consistently.
    
    Args:
        data: Data to format
        template: Optional template string for formatting
        max_length: Maximum response length before truncation
    
    Returns:
        Formatted CallToolResult
    """
    try:
        if template:
            text = template.format(data=data)
        elif isinstance(data, (list, tuple)):
            if not data:
                text = "No results found."
            else:
                text = "\n".join(str(item) for item in data[:50])  # Limit to 50 items
                if len(data) > 50:
                    text += f"\n\n... and {len(data) - 50} more items"
        elif isinstance(data, dict):
            # Format dict as readable text
            lines = []
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    lines.append(f"{key}: {value}")
                elif isinstance(value, (list, tuple)) and len(value) <= 3:
                    lines.append(f"{key}: {', '.join(str(v) for v in value)}")
                else:
                    lines.append(f"{key}: {type(value).__name__}")
            text = "\n".join(lines)
        else:
            text = str(data)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length - 50] + "\n\n[Response truncated due to length]"
        
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=text
                )
            ]
        )
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Error formatting response: {str(e)}"
                )
            ]
        )