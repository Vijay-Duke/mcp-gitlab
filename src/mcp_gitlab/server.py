import os
import json
import logging
from typing import Any, List, Optional

try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError as e:
    import sys
    print(f"Error importing MCP: {e}", file=sys.stderr)
    raise ImportError(f"Failed to import MCP SDK. Make sure 'mcp' is installed: {e}")

from pydantic import AnyUrl
from dotenv import load_dotenv
import gitlab.exceptions

try:
    from .gitlab_client import GitLabClient, GitLabConfig
    from .git_detector import GitDetector
    from .utils import GitLabClientManager, sanitize_error, truncate_response
    from .gitlab_client import GitLabClient, GitLabConfig
    from .utils import GitLabClientManager, sanitize_error, truncate_response
    from .constants import (
        DEFAULT_GITLAB_URL, MAX_RESPONSE_SIZE, LOG_LEVEL, LOG_FORMAT,
        JSON_LOGGING, ERROR_NO_TOKEN, ERROR_AUTH_FAILED, ERROR_NOT_FOUND,
        ERROR_RATE_LIMIT, ERROR_GENERIC, ERROR_INVALID_INPUT,
    )
    from .tool_handlers import TOOL_HANDLERS
except ImportError as e:
    # Fallback imports for development/testing when package is not installed
    import sys
    import os
    from pathlib import Path
    
    # Add the parent directory to sys.path to allow imports
    src_path = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_path))
    
    try:
        from mcp_gitlab.gitlab_client import GitLabClient, GitLabConfig
        from mcp_gitlab.git_detector import GitDetector
        from mcp_gitlab.utils import GitLabClientManager, sanitize_error, truncate_response
        from mcp_gitlab.constants import (
            DEFAULT_GITLAB_URL, DEFAULT_PAGE_SIZE, SMALL_PAGE_SIZE, MAX_PAGE_SIZE,
            DEFAULT_MAX_BODY_LENGTH, MAX_RESPONSE_SIZE, LOG_LEVEL, LOG_FORMAT,
            JSON_LOGGING, ERROR_NO_TOKEN, ERROR_AUTH_FAILED, ERROR_NOT_FOUND,
            ERROR_RATE_LIMIT, ERROR_GENERIC, ERROR_NO_PROJECT, ERROR_INVALID_INPUT,
            TOOL_LIST_PROJECTS, TOOL_GET_PROJECT, TOOL_GET_CURRENT_PROJECT,
            TOOL_LIST_ISSUES, TOOL_LIST_MRS, TOOL_GET_MR_NOTES,
            TOOL_LIST_BRANCHES, TOOL_LIST_PIPELINES,
            TOOL_LIST_COMMITS, TOOL_LIST_REPOSITORY_TREE, TOOL_LIST_TAGS,
            TOOL_LIST_USER_EVENTS, TOOL_LIST_PROJECT_MEMBERS, TOOL_LIST_PROJECT_HOOKS,
            TOOL_LIST_RELEASES, TOOL_GET_CURRENT_USER, TOOL_GET_USER,
            TOOL_LIST_GROUPS, TOOL_GET_GROUP, TOOL_LIST_GROUP_PROJECTS,
            TOOL_LIST_SNIPPETS, TOOL_GET_SNIPPET, TOOL_CREATE_SNIPPET,
            TOOL_UPDATE_SNIPPET, TOOL_LIST_PIPELINE_JOBS, TOOL_DOWNLOAD_JOB_ARTIFACT, TOOL_LIST_PROJECT_JOBS
        )
        from mcp_gitlab.tool_handlers import TOOL_HANDLERS, get_project_id_or_detect
        import mcp_gitlab.tool_descriptions as desc
    except ImportError:
        # If mcp_gitlab package doesn't exist, try direct imports
        from gitlab_client import GitLabClient, GitLabConfig
        from git_detector import GitDetector
        from utils import GitLabClientManager, sanitize_error, truncate_response
        from constants import (
            DEFAULT_GITLAB_URL, DEFAULT_PAGE_SIZE, SMALL_PAGE_SIZE, MAX_PAGE_SIZE,
            DEFAULT_MAX_BODY_LENGTH, MAX_RESPONSE_SIZE, LOG_LEVEL, LOG_FORMAT,
            JSON_LOGGING, ERROR_NO_TOKEN, ERROR_AUTH_FAILED, ERROR_NOT_FOUND,
            ERROR_RATE_LIMIT, ERROR_GENERIC, ERROR_NO_PROJECT, ERROR_INVALID_INPUT,
            TOOL_LIST_PROJECTS, TOOL_GET_PROJECT, TOOL_GET_CURRENT_PROJECT,
            TOOL_LIST_ISSUES, TOOL_LIST_MRS, TOOL_GET_MR_NOTES,
            TOOL_LIST_BRANCHES, TOOL_LIST_PIPELINES,
            TOOL_LIST_COMMITS, TOOL_LIST_REPOSITORY_TREE, TOOL_LIST_TAGS,
            TOOL_LIST_USER_EVENTS, TOOL_LIST_PROJECT_MEMBERS, TOOL_LIST_PROJECT_HOOKS,
            TOOL_LIST_RELEASES, TOOL_GET_CURRENT_USER, TOOL_GET_USER,
            TOOL_LIST_GROUPS, TOOL_GET_GROUP, TOOL_LIST_GROUP_PROJECTS,
            TOOL_LIST_SNIPPETS, TOOL_GET_SNIPPET, TOOL_CREATE_SNIPPET,
            TOOL_UPDATE_SNIPPET, TOOL_LIST_PIPELINE_JOBS, TOOL_DOWNLOAD_JOB_ARTIFACT, TOOL_LIST_PROJECT_JOBS
        )
        from tool_handlers import TOOL_HANDLERS, get_project_id_or_detect
        import tool_descriptions as desc

load_dotenv()

# Configure logging based on environment settings
if JSON_LOGGING:
    # Use python-json-logger for structured logging
    from pythonjsonlogger import jsonlogger
    
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={'timestamp': 'asctime', 'level': 'levelname'}
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    logging.root.handlers = [handler]
    logging.root.setLevel(getattr(logging, LOG_LEVEL.upper()))
else:
    # Use traditional logging format
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT
    )

logger = logging.getLogger(__name__)

server = Server("mcp-gitlab")
client_manager = GitLabClientManager()


def get_gitlab_client() -> GitLabClient:
    """Get GitLab client using singleton manager"""
    config = GitLabConfig(
        url=os.getenv("GITLAB_URL", DEFAULT_GITLAB_URL),
        private_token=os.getenv("GITLAB_PRIVATE_TOKEN"),
        oauth_token=os.getenv("GITLAB_OAUTH_TOKEN")
    )
    return client_manager.get_client(config)




from .tool_definitions import TOOLS

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available GitLab tools"""
    return TOOLS


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution with comprehensive error handling"""
    try:
        client = get_gitlab_client()
        
        # Check if tool exists
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            raise ValueError(f"Unknown tool: {name}")
        
        # Execute the handler
        result = handler(client, arguments)
        
        # Truncate response if too large
        result = truncate_response(result, MAX_RESPONSE_SIZE)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except gitlab.exceptions.GitlabAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        error_response = sanitize_error(e, ERROR_AUTH_FAILED)
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]
    except gitlab.exceptions.GitlabGetError as e:
        response_code = getattr(e, 'response_code', None)
        if response_code == 404:
            logger.warning(f"Resource not found: {e}")
            error_response = sanitize_error(e, ERROR_NOT_FOUND)
        elif response_code == 429:
            logger.warning(f"Rate limit exceeded: {e}")
            error_response = sanitize_error(e, ERROR_RATE_LIMIT)
        else:
            logger.error(f"GitLab API error: {e}")
            error_response = sanitize_error(e)
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]
    except gitlab.exceptions.GitlabError as e:
        logger.error(f"General GitLab error: {e}")
        error_response = sanitize_error(e)
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        error_response = sanitize_error(e, ERROR_INVALID_INPUT)
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        error_response = sanitize_error(e, ERROR_GENERIC)
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def main():
    """Run the robust MCP GitLab server"""
    try:
        logger.info("Starting robust MCP GitLab server...")
        
        if not (os.getenv("GITLAB_PRIVATE_TOKEN") or os.getenv("GITLAB_OAUTH_TOKEN")):
            logger.warning(ERROR_NO_TOKEN)
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Server streams initialized")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-gitlab-robust",
                    server_version="2.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)