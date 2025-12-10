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
    from .constants import (
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
        TOOL_UPDATE_SNIPPET, TOOL_LIST_PIPELINE_JOBS, TOOL_DOWNLOAD_JOB_ARTIFACT, TOOL_LIST_PROJECT_JOBS,
        TOOL_SEARCH_USER, TOOL_GET_USER_DETAILS, TOOL_GET_MY_PROFILE,
        TOOL_GET_USER_CONTRIBUTIONS_SUMMARY, TOOL_GET_USER_ACTIVITY_FEED,
        TOOL_GET_USER_OPEN_MRS, TOOL_GET_USER_REVIEW_REQUESTS, TOOL_GET_USER_OPEN_ISSUES,
        TOOL_GET_USER_REPORTED_ISSUES, TOOL_GET_USER_RESOLVED_ISSUES,
        TOOL_GET_USER_COMMITS, TOOL_GET_USER_MERGE_COMMITS,
        TOOL_GET_USER_CODE_CHANGES_SUMMARY, TOOL_GET_USER_SNIPPETS,
        TOOL_GET_USER_ISSUE_COMMENTS, TOOL_GET_USER_MR_COMMENTS,
        TOOL_GET_USER_DISCUSSION_THREADS, TOOL_GET_USER_RESOLVED_THREADS
    )
    from .tool_handlers import TOOL_HANDLERS, get_project_id_or_detect
    from . import tool_descriptions as desc
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
            TOOL_UPDATE_SNIPPET, TOOL_LIST_PIPELINE_JOBS, TOOL_DOWNLOAD_JOB_ARTIFACT, TOOL_LIST_PROJECT_JOBS,
            TOOL_SEARCH_USER, TOOL_GET_USER_DETAILS, TOOL_GET_MY_PROFILE,
            TOOL_GET_USER_CONTRIBUTIONS_SUMMARY, TOOL_GET_USER_ACTIVITY_FEED,
            TOOL_GET_USER_OPEN_MRS, TOOL_GET_USER_REVIEW_REQUESTS, TOOL_GET_USER_OPEN_ISSUES,
            TOOL_GET_USER_REPORTED_ISSUES, TOOL_GET_USER_RESOLVED_ISSUES,
            TOOL_GET_USER_COMMITS, TOOL_GET_USER_MERGE_COMMITS,
            TOOL_GET_USER_CODE_CHANGES_SUMMARY, TOOL_GET_USER_SNIPPETS,
            TOOL_GET_USER_ISSUE_COMMENTS, TOOL_GET_USER_MR_COMMENTS,
            TOOL_GET_USER_DISCUSSION_THREADS, TOOL_GET_USER_RESOLVED_THREADS
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
            TOOL_UPDATE_SNIPPET, TOOL_LIST_PIPELINE_JOBS, TOOL_DOWNLOAD_JOB_ARTIFACT, TOOL_LIST_PROJECT_JOBS,
            TOOL_SEARCH_USER, TOOL_GET_USER_DETAILS, TOOL_GET_MY_PROFILE,
            TOOL_GET_USER_CONTRIBUTIONS_SUMMARY, TOOL_GET_USER_ACTIVITY_FEED,
            TOOL_GET_USER_OPEN_MRS, TOOL_GET_USER_REVIEW_REQUESTS, TOOL_GET_USER_OPEN_ISSUES,
            TOOL_GET_USER_REPORTED_ISSUES, TOOL_GET_USER_RESOLVED_ISSUES,
            TOOL_GET_USER_COMMITS, TOOL_GET_USER_MERGE_COMMITS,
            TOOL_GET_USER_CODE_CHANGES_SUMMARY, TOOL_GET_USER_SNIPPETS,
            TOOL_GET_USER_ISSUE_COMMENTS, TOOL_GET_USER_MR_COMMENTS,
            TOOL_GET_USER_DISCUSSION_THREADS, TOOL_GET_USER_RESOLVED_THREADS
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




@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available GitLab tools"""
    return [
        # Project Management
        types.Tool(
            name=TOOL_LIST_PROJECTS,
            description=desc.DESC_LIST_PROJECTS,
            inputSchema={
                "type": "object",
                "properties": {
                    "owned": {"type": "boolean", "description": desc.DESC_OWNED_PROJECTS, "default": False},
                    "search": {"type": "string", "description": desc.DESC_SEARCH_TERM + " for projects"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_PROJECT,
            description=desc.DESC_GET_PROJECT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID_REQUIRED}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name=TOOL_GET_CURRENT_PROJECT,
            description=desc.DESC_GET_CURRENT_PROJECT,
            inputSchema={
                "type": "object", 
                "properties": {
                    "path": {"type": "string", "description": desc.DESC_GIT_PATH}
                }
            }
        ),
        
        # Authentication & User Info
        types.Tool(
            name=TOOL_GET_CURRENT_USER,
            description=desc.DESC_GET_CURRENT_USER,
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name=TOOL_GET_USER,
            description=desc.DESC_GET_USER,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": desc.DESC_USER_ID},
                    "username": {"type": "string", "description": desc.DESC_USERNAME}
                }
            }
        ),
        
        # Group Management
        types.Tool(
            name=TOOL_LIST_GROUPS,
            description=desc.DESC_LIST_GROUPS,
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": desc.DESC_SEARCH_TERM + " for groups"},
                    "owned": {"type": "boolean", "description": desc.DESC_OWNED_GROUPS, "default": False},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_GROUP,
            description=desc.DESC_GET_GROUP,
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string", "description": desc.DESC_GROUP_ID},
                    "with_projects": {"type": "boolean", "description": desc.DESC_WITH_PROJECTS, "default": False}
                },
                "required": ["group_id"]
            }
        ),
        types.Tool(
            name=TOOL_LIST_GROUP_PROJECTS,
            description=desc.DESC_LIST_GROUP_PROJECTS,
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string", "description": desc.DESC_GROUP_ID},
                    "search": {"type": "string", "description": desc.DESC_SEARCH_TERM + " for projects"},
                    "include_subgroups": {"type": "boolean", "description": desc.DESC_INCLUDE_SUBGROUPS, "default": False},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["group_id"]
            }
        ),
        
        # Issues
        types.Tool(
            name=TOOL_LIST_ISSUES,
            description=desc.DESC_LIST_ISSUES,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "state": {"type": "string", "description": desc.DESC_STATE_ISSUE, "enum": ["opened", "closed", "all"], "default": "opened"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name="gitlab_get_issue",
            description=desc.DESC_GET_ISSUE,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "issue_iid": {"type": "integer", "description": desc.DESC_ISSUE_IID}
                },
                "required": ["issue_iid"]
            }
        ),
        
        # Merge Requests  
        types.Tool(
            name=TOOL_LIST_MRS,
            description=desc.DESC_LIST_MRS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "state": {"type": "string", "description": desc.DESC_STATE_MR, "enum": ["opened", "closed", "merged", "all"], "default": "opened"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name="gitlab_get_merge_request",
            description=desc.DESC_GET_MR,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID}
                },
                "required": ["mr_iid"]
            }
        ),
        types.Tool(
            name=TOOL_GET_MR_NOTES,
            description=desc.DESC_GET_MR_NOTES,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": SMALL_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1},
                    "sort": {"type": "string", "description": desc.DESC_SORT_ORDER, "enum": ["asc", "desc"], "default": "asc"},
                    "order_by": {"type": "string", "description": desc.DESC_ORDER_BY, "enum": ["created_at", "updated_at"], "default": "created_at"},
                    "max_body_length": {"type": "integer", "description": desc.DESC_MAX_BODY_LENGTH, "default": DEFAULT_MAX_BODY_LENGTH, "minimum": 0}
                },
                "required": ["mr_iid"]
            }
        ),
        
        # Repository Files
        types.Tool(
            name="gitlab_get_file_content",
            description=desc.DESC_GET_FILE_CONTENT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "file_path": {"type": "string", "description": desc.DESC_FILE_PATH},
                    "ref": {"type": "string", "description": desc.DESC_REF}
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name=TOOL_LIST_REPOSITORY_TREE,
            description=desc.DESC_LIST_TREE,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "path": {"type": "string", "description": desc.DESC_TREE_PATH, "default": ""},
                    "ref": {"type": "string", "description": desc.DESC_REF},
                    "recursive": {"type": "boolean", "description": desc.DESC_RECURSIVE, "default": False}
                }
            }
        ),
        
        # Snippets
        types.Tool(
            name=TOOL_LIST_SNIPPETS,
            description=desc.DESC_LIST_SNIPPETS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_SNIPPET,
            description=desc.DESC_GET_SNIPPET,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "snippet_id": {"type": "integer", "description": desc.DESC_SNIPPET_ID}
                },
                "required": ["snippet_id"]
            }
        ),
        types.Tool(
            name=TOOL_CREATE_SNIPPET,
            description=desc.DESC_CREATE_SNIPPET,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "title": {"type": "string", "description": desc.DESC_SNIPPET_TITLE},
                    "file_name": {"type": "string", "description": desc.DESC_SNIPPET_FILE_NAME},
                    "content": {"type": "string", "description": desc.DESC_SNIPPET_CONTENT},
                    "description": {"type": "string", "description": desc.DESC_SNIPPET_DESCRIPTION},
                    "visibility": {"type": "string", "description": desc.DESC_SNIPPET_VISIBILITY, "enum": ["private", "internal", "public"], "default": "private"}
                },
                "required": ["title", "file_name", "content"]
            }
        ),
        types.Tool(
            name=TOOL_UPDATE_SNIPPET,
            description=desc.DESC_UPDATE_SNIPPET,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "snippet_id": {"type": "integer", "description": desc.DESC_SNIPPET_ID},
                    "title": {"type": "string", "description": desc.DESC_SNIPPET_TITLE},
                    "file_name": {"type": "string", "description": desc.DESC_SNIPPET_FILE_NAME},
                    "content": {"type": "string", "description": desc.DESC_SNIPPET_CONTENT},
                    "description": {"type": "string", "description": desc.DESC_SNIPPET_DESCRIPTION},
                    "visibility": {"type": "string", "description": desc.DESC_SNIPPET_VISIBILITY, "enum": ["private", "internal", "public"]}
                },
                "required": ["snippet_id"]
            }
        ),
        
        # Commits
        types.Tool(
            name=TOOL_LIST_COMMITS,
            description=desc.DESC_LIST_COMMITS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "ref_name": {"type": "string", "description": desc.DESC_REF.replace("commit SHA", "tag name")},
                    "since": {"type": "string", "description": desc.DESC_DATE_SINCE},
                    "until": {"type": "string", "description": desc.DESC_DATE_UNTIL},
                    "path": {"type": "string", "description": desc.DESC_PATH_FILTER},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name="gitlab_get_commit",
            description=desc.DESC_GET_COMMIT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "commit_sha": {"type": "string", "description": desc.DESC_COMMIT_SHA},
                    "include_stats": {"type": "boolean", "description": desc.DESC_INCLUDE_STATS, "default": False}
                },
                "required": ["commit_sha"]
            }
        ),
        types.Tool(
            name="gitlab_get_commit_diff",
            description=desc.DESC_GET_COMMIT_DIFF,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "commit_sha": {"type": "string", "description": "Commit SHA"}
                },
                "required": ["commit_sha"]
            }
        ),
        
        # Search
        types.Tool(
            name="gitlab_search_projects",
            description=desc.DESC_SEARCH_PROJECTS,
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": desc.DESC_SEARCH_TERM},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["search"]
            }
        ),
        types.Tool(
            name="gitlab_search_in_project",
            description=desc.DESC_SEARCH_IN_PROJECT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "scope": {"type": "string", "description": desc.DESC_SEARCH_SCOPE, "enum": ["issues", "merge_requests", "milestones", "notes", "wiki_blobs", "commits", "blobs"]},
                    "search": {"type": "string", "description": desc.DESC_SEARCH_TERM},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["scope", "search"]
            }
        ),
        
        # Repository Info
        types.Tool(
            name=TOOL_LIST_BRANCHES,
            description=desc.DESC_LIST_BRANCHES,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID or path (optional - auto-detects from git)"}
                }
            }
        ),
        types.Tool(
            name=TOOL_LIST_PIPELINES,
            description=desc.DESC_LIST_PIPELINES,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "ref": {"type": "string", "description": desc.DESC_BRANCH_TAG_REF}
                }
            }
        ),
        
        # User Events
        types.Tool(
            name=TOOL_LIST_USER_EVENTS,
            description=desc.DESC_LIST_USER_EVENTS,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": desc.DESC_USERNAME},
                    "action": {"type": "string", "description": desc.DESC_ACTION_FILTER, "enum": ["commented", "pushed", "created", "closed", "opened", "merged", "joined", "left", "destroyed", "expired", "removed", "deleted", "approved", "updated", "uploaded", "downloaded"]},
                    "target_type": {"type": "string", "description": desc.DESC_TARGET_TYPE_FILTER, "enum": ["Note", "Issue", "MergeRequest", "Commit", "Project", "Snippet", "User", "WikiPage", "Milestone", "Discussion", "DiffNote"]},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1},
                    "after": {"type": "string", "description": desc.DESC_DATE_AFTER},
                    "before": {"type": "string", "description": desc.DESC_DATE_BEFORE}
                },
                "required": ["username"]
            }
        ),
        
        # MR Lifecycle Tools
        types.Tool(
            name="gitlab_update_merge_request",
            description=desc.DESC_UPDATE_MR,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID},
                    "title": {"type": "string", "description": desc.DESC_TITLE},
                    "description": {"type": "string", "description": desc.DESC_DESCRIPTION},
                    "assignee_id": {"type": "integer", "description": desc.DESC_ASSIGNEE_ID},
                    "assignee_ids": {"type": "array", "items": {"type": "integer"}, "description": desc.DESC_ASSIGNEE_IDS},
                    "reviewer_ids": {"type": "array", "items": {"type": "integer"}, "description": desc.DESC_REVIEWER_IDS},
                    "labels": {"type": "string", "description": desc.DESC_LABELS},
                    "milestone_id": {"type": "integer", "description": desc.DESC_MILESTONE_ID},
                    "state_event": {"type": "string", "description": desc.DESC_STATE_EVENT, "enum": ["close", "reopen"]},
                    "remove_source_branch": {"type": "boolean", "description": desc.DESC_REMOVE_SOURCE_BRANCH},
                    "squash": {"type": "boolean", "description": desc.DESC_SQUASH},
                    "discussion_locked": {"type": "boolean", "description": desc.DESC_DISCUSSION_LOCKED},
                    "allow_collaboration": {"type": "boolean", "description": desc.DESC_ALLOW_COLLABORATION},
                    "target_branch": {"type": "string", "description": desc.DESC_TARGET_BRANCH}
                },
                "required": ["mr_iid"]
            }
        ),
        types.Tool(
            name="gitlab_close_merge_request",
            description=desc.DESC_CLOSE_MR,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID}
                },
                "required": ["mr_iid"]
            }
        ),
        types.Tool(
            name="gitlab_merge_merge_request",
            description=desc.DESC_MERGE_MR,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID},
                    "merge_when_pipeline_succeeds": {"type": "boolean", "description": desc.DESC_MERGE_WHEN_PIPELINE_SUCCEEDS, "default": False},
                    "should_remove_source_branch": {"type": "boolean", "description": desc.DESC_REMOVE_SOURCE_BRANCH},
                    "merge_commit_message": {"type": "string", "description": desc.DESC_MERGE_COMMIT_MESSAGE},
                    "squash_commit_message": {"type": "string", "description": desc.DESC_SQUASH_COMMIT_MESSAGE},
                    "squash": {"type": "boolean", "description": desc.DESC_SQUASH}
                },
                "required": ["mr_iid"]
            }
        ),
        
        # Comment Tools
        types.Tool(
            name="gitlab_add_issue_comment",
            description=desc.DESC_ADD_ISSUE_COMMENT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "issue_iid": {"type": "integer", "description": desc.DESC_ISSUE_IID},
                    "body": {"type": "string", "description": desc.DESC_COMMENT_BODY}
                },
                "required": ["issue_iid", "body"]
            }
        ),
        types.Tool(
            name="gitlab_add_merge_request_comment",
            description=desc.DESC_ADD_MR_COMMENT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID},
                    "body": {"type": "string", "description": desc.DESC_COMMENT_BODY}
                },
                "required": ["mr_iid", "body"]
            }
        ),
        
        # Approval Tools
        types.Tool(
            name="gitlab_approve_merge_request",
            description=desc.DESC_APPROVE_MR,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID}
                },
                "required": ["mr_iid"]
            }
        ),
        types.Tool(
            name="gitlab_get_merge_request_approvals",
            description=desc.DESC_GET_MR_APPROVALS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID}
                },
                "required": ["mr_iid"]
            }
        ),
        
        # Repository Tools
        types.Tool(
            name=TOOL_LIST_TAGS,
            description=desc.DESC_LIST_TAGS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "order_by": {"type": "string", "description": desc.DESC_ORDER_BY_TAG, "enum": ["name", "updated", "version", "semver"], "default": "updated"},
                    "sort": {"type": "string", "description": desc.DESC_SORT_ORDER, "enum": ["asc", "desc"], "default": "desc"}
                }
            }
        ),
        types.Tool(
            name="gitlab_create_commit",
            description=desc.DESC_CREATE_COMMIT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "branch": {"type": "string", "description": desc.DESC_BRANCH},
                    "commit_message": {"type": "string", "description": desc.DESC_COMMIT_MESSAGE},
                    "actions": {
                        "type": "array",
                        "description": desc.DESC_ACTIONS,
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["create", "update", "delete", "move"]},
                                "file_path": {"type": "string"},
                                "content": {"type": "string"},
                                "previous_path": {"type": "string"},
                                "encoding": {"type": "string", "enum": ["text", "base64"], "default": "text"}
                            },
                            "required": ["action", "file_path"]
                        }
                    },
                    "author_email": {"type": "string", "description": desc.DESC_AUTHOR_EMAIL},
                    "author_name": {"type": "string", "description": desc.DESC_AUTHOR_NAME}
                },
                "required": ["branch", "commit_message", "actions"]
            }
        ),
        types.Tool(
            name="gitlab_compare_refs",
            description=desc.DESC_COMPARE_REFS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "from_ref": {"type": "string", "description": desc.DESC_FROM_REF},
                    "to_ref": {"type": "string", "description": desc.DESC_TO_REF},
                    "straight": {"type": "boolean", "description": desc.DESC_STRAIGHT, "default": False}
                },
                "required": ["from_ref", "to_ref"]
            }
        ),
        
        # Release and Member Tools
        types.Tool(
            name=TOOL_LIST_RELEASES,
            description=desc.DESC_LIST_RELEASES,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "order_by": {"type": "string", "description": desc.DESC_ORDER_BY, "enum": ["released_at", "created_at"], "default": "released_at"},
                    "sort": {"type": "string", "description": desc.DESC_SORT_ORDER, "enum": ["asc", "desc"], "default": "desc"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_LIST_PROJECT_MEMBERS,
            description=desc.DESC_LIST_PROJECT_MEMBERS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "query": {"type": "string", "description": desc.DESC_QUERY},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_LIST_PROJECT_HOOKS,
            description=desc.DESC_LIST_PROJECT_HOOKS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID}
                }
            }
        ),
        
        # MR Advanced Tools
        types.Tool(
            name="gitlab_get_merge_request_discussions",
            description=desc.DESC_GET_MR_DISCUSSIONS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["mr_iid"]
            }
        ),
        types.Tool(
            name="gitlab_resolve_discussion",
            description=desc.DESC_RESOLVE_DISCUSSION,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID},
                    "discussion_id": {"type": "string", "description": desc.DESC_DISCUSSION_ID}
                },
                "required": ["mr_iid", "discussion_id"]
            }
        ),
        types.Tool(
            name="gitlab_get_merge_request_changes",
            description=desc.DESC_GET_MR_CHANGES,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID}
                },
                "required": ["mr_iid"]
            }
        ),
        
        # MR Operations Tools
        types.Tool(
            name="gitlab_rebase_merge_request",
            description=desc.DESC_REBASE_MR,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID}
                },
                "required": ["mr_iid"]
            }
        ),
        types.Tool(
            name="gitlab_cherry_pick_commit",
            description=desc.DESC_CHERRY_PICK,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "commit_sha": {"type": "string", "description": desc.DESC_COMMIT_SHA},
                    "branch": {"type": "string", "description": desc.DESC_BRANCH}
                },
                "required": ["commit_sha", "branch"]
            }
        ),
        
        # AI Helper Tools
        types.Tool(
            name="gitlab_summarize_merge_request",
            description=desc.DESC_SUMMARIZE_MR,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "mr_iid": {"type": "integer", "description": desc.DESC_MR_IID},
                    "max_length": {"type": "integer", "description": desc.DESC_MAX_LENGTH, "default": 500}
                },
                "required": ["mr_iid"]
            }
        ),
        types.Tool(
            name="gitlab_summarize_issue",
            description=desc.DESC_SUMMARIZE_ISSUE,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "issue_iid": {"type": "integer", "description": desc.DESC_ISSUE_IID},
                    "max_length": {"type": "integer", "description": desc.DESC_MAX_LENGTH, "default": 500}
                },
                "required": ["issue_iid"]
            }
        ),
        types.Tool(
            name="gitlab_summarize_pipeline",
            description=desc.DESC_SUMMARIZE_PIPELINE,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "pipeline_id": {"type": "integer", "description": desc.DESC_PIPELINE_ID},
                    "max_length": {"type": "integer", "description": desc.DESC_MAX_LENGTH, "default": 500}
                },
                "required": ["pipeline_id"]
            }
        ),
        
        # Advanced Diff Tools
        types.Tool(
            name="gitlab_smart_diff",
            description=desc.DESC_SMART_DIFF,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "from_ref": {"type": "string", "description": desc.DESC_FROM_REF},
                    "to_ref": {"type": "string", "description": desc.DESC_TO_REF},
                    "context_lines": {"type": "integer", "description": desc.DESC_CONTEXT_LINES, "default": 3},
                    "max_file_size": {"type": "integer", "description": desc.DESC_MAX_FILE_SIZE, "default": 50000}
                },
                "required": ["from_ref", "to_ref"]
            }
        ),
        types.Tool(
            name="gitlab_safe_preview_commit",
            description=desc.DESC_SAFE_PREVIEW_COMMIT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "branch": {"type": "string", "description": desc.DESC_BRANCH},
                    "commit_message": {"type": "string", "description": desc.DESC_COMMIT_MESSAGE},
                    "actions": {
                        "type": "array",
                        "description": desc.DESC_ACTIONS,
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["create", "update", "delete", "move"]},
                                "file_path": {"type": "string"},
                                "content": {"type": "string"},
                                "previous_path": {"type": "string"},
                                "encoding": {"type": "string", "enum": ["text", "base64"], "default": "text"}
                            },
                            "required": ["action", "file_path"]
                        }
                    }
                },
                "required": ["branch", "commit_message", "actions"]
            }
        ),
        
        # Batch Operations Tool
        types.Tool(
            name="gitlab_batch_operations",
            description=desc.DESC_BATCH_OPERATIONS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "operations": {
                        "type": "array",
                        "description": desc.DESC_OPERATIONS,
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Operation name for reference"},
                                "tool": {"type": "string", "description": "GitLab tool name to execute"},
                                "arguments": {"type": "object", "description": "Arguments for the tool"}
                            },
                            "required": ["name", "tool", "arguments"]
                        }
                    },
                    "stop_on_error": {"type": "boolean", "description": desc.DESC_STOP_ON_ERROR, "default": True}
                },
                "required": ["operations"]
            }
        ),
        
        # Job and Artifact Tools
        types.Tool(
            name=TOOL_LIST_PIPELINE_JOBS,
            description=desc.DESC_LIST_PIPELINE_JOBS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "pipeline_id": {"type": "integer", "description": desc.DESC_PIPELINE_ID},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["pipeline_id"]
            }
        ),
        types.Tool(
            name=TOOL_DOWNLOAD_JOB_ARTIFACT,
            description=desc.DESC_DOWNLOAD_JOB_ARTIFACT,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "job_id": {"type": "integer", "description": desc.DESC_JOB_ID},
                    "artifact_path": {"type": "string", "description": desc.DESC_ARTIFACT_PATH}
                },
                "required": ["job_id"]
            }
        ),
        types.Tool(
            name=TOOL_LIST_PROJECT_JOBS,
            description=desc.DESC_LIST_PROJECT_JOBS,
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": desc.DESC_PROJECT_ID},
                    "scope": {"type": "string", "description": desc.DESC_JOB_SCOPE, "enum": ["created", "pending", "running", "failed", "success", "canceled", "skipped", "waiting_for_resource", "manual"]},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        
        # User & Profile Tools
        types.Tool(
            name=TOOL_SEARCH_USER,
            description=desc.DESC_SEARCH_USER,
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Search query (name, username, or email fragment)"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["search"]
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_DETAILS,
            description=desc.DESC_GET_USER_DETAILS,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_MY_PROFILE,
            description=desc.DESC_GET_MY_PROFILE,
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_CONTRIBUTIONS_SUMMARY,
            description=desc.DESC_GET_USER_CONTRIBUTIONS_SUMMARY,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "since": {"type": "string", "description": "Start date for analysis (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "End date for analysis (YYYY-MM-DD)"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_ACTIVITY_FEED,
            description=desc.DESC_GET_USER_ACTIVITY_FEED,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "action": {"type": "string", "description": "Filter by action type"},
                    "target_type": {"type": "string", "description": "Filter by target type"},
                    "after": {"type": "string", "description": "Events after this date (YYYY-MM-DD)"},
                    "before": {"type": "string", "description": "Events before this date (YYYY-MM-DD)"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        
        # User's Issues & MRs Tools
        types.Tool(
            name=TOOL_GET_USER_OPEN_MRS,
            description=desc.DESC_GET_USER_OPEN_MRS,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "sort": {"type": "string", "description": "Sort order", "enum": ["updated", "created", "priority"], "default": "updated"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_REVIEW_REQUESTS,
            description=desc.DESC_GET_USER_REVIEW_REQUESTS,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "priority": {"type": "string", "description": "Filter by priority", "enum": ["high", "medium", "low"]},
                    "sort": {"type": "string", "description": "Sort order", "enum": ["urgency", "age", "project"], "default": "urgency"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_OPEN_ISSUES,
            description=desc.DESC_GET_USER_OPEN_ISSUES,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "severity": {"type": "string", "description": "Filter by severity level"},
                    "sla_status": {"type": "string", "description": "Filter by SLA compliance", "enum": ["at_risk", "overdue", "ok"]},
                    "sort": {"type": "string", "description": "Sort order", "enum": ["priority", "due_date", "updated"], "default": "priority"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_REPORTED_ISSUES,
            description=desc.DESC_GET_USER_REPORTED_ISSUES,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "state": {"type": "string", "description": "Filter by state", "enum": ["opened", "closed", "all"], "default": "opened"},
                    "since": {"type": "string", "description": "Issues created after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Issues created before date (YYYY-MM-DD)"},
                    "sort": {"type": "string", "description": "Sort order", "enum": ["created", "updated", "closed"], "default": "created"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_RESOLVED_ISSUES,
            description=desc.DESC_GET_USER_RESOLVED_ISSUES,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "since": {"type": "string", "description": "Resolved after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Resolved before date (YYYY-MM-DD)"},
                    "complexity": {"type": "string", "description": "Filter by resolution complexity"},
                    "sort": {"type": "string", "description": "Sort order", "enum": ["closed", "complexity", "impact"], "default": "closed"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        
        # User's Code & Commits Tools
        types.Tool(
            name=TOOL_GET_USER_COMMITS,
            description=desc.DESC_GET_USER_COMMITS,
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Numeric user ID"},
                    "username": {"type": "string", "description": "Username string"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"},
                    "branch": {"type": "string", "description": "Filter by specific branch"},
                    "since": {"type": "string", "description": "Commits after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Commits before date (YYYY-MM-DD)"},
                    "include_stats": {"type": "boolean", "description": "Include file change statistics", "default": False},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                }
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_MERGE_COMMITS,
            description=desc.DESC_GET_USER_MERGE_COMMITS,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username string"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"},
                    "since": {"type": "string", "description": "Commits after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Commits before date (YYYY-MM-DD)"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_CODE_CHANGES_SUMMARY,
            description=desc.DESC_GET_USER_CODE_CHANGES_SUMMARY,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username string"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"},
                    "since": {"type": "string", "description": "Commits after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Commits before date (YYYY-MM-DD)"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_SNIPPETS,
            description=desc.DESC_GET_USER_SNIPPETS,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username string"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_ISSUE_COMMENTS,
            description=desc.DESC_GET_USER_ISSUE_COMMENTS,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username string"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"},
                    "since": {"type": "string", "description": "Comments after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Comments before date (YYYY-MM-DD)"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_MR_COMMENTS,
            description=desc.DESC_GET_USER_MR_COMMENTS,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username string"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"},
                    "since": {"type": "string", "description": "Comments after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Comments before date (YYYY-MM-DD)"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_DISCUSSION_THREADS,
            description=desc.DESC_GET_USER_DISCUSSION_THREADS,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username string"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"},
                    "thread_status": {"type": "string", "description": "Filter by thread status", "enum": ["resolved", "unresolved"]},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name=TOOL_GET_USER_RESOLVED_THREADS,
            description=desc.DESC_GET_USER_RESOLVED_THREADS,
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username string"},
                    "project_id": {"type": "string", "description": "Optional project scope filter"},
                    "since": {"type": "string", "description": "Threads resolved after date (YYYY-MM-DD)"},
                    "until": {"type": "string", "description": "Threads resolved before date (YYYY-MM-DD)"},
                    "per_page": {"type": "integer", "description": desc.DESC_PER_PAGE, "default": DEFAULT_PAGE_SIZE, "minimum": 1, "maximum": MAX_PAGE_SIZE},
                    "page": {"type": "integer", "description": desc.DESC_PAGE_NUMBER, "default": 1, "minimum": 1}
                },
                "required": ["username"]
            }
        )
    ]


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