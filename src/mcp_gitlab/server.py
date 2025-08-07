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
        TOOL_LIST_PROJECTS, TOOL_GET_PROJECT, TOOL_DETECT_PROJECT, TOOL_GET_CURRENT_PROJECT,
        TOOL_LIST_ISSUES, TOOL_LIST_MRS, TOOL_GET_MR_NOTES,
        TOOL_LIST_BRANCHES, TOOL_LIST_PIPELINES, TOOL_GET_USER_EVENTS,
        TOOL_LIST_COMMITS, TOOL_LIST_REPOSITORY_TREE, TOOL_LIST_TAGS,
        TOOL_LIST_USER_EVENTS, TOOL_LIST_PROJECT_MEMBERS, TOOL_LIST_PROJECT_HOOKS,
        TOOL_LIST_RELEASES
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
            TOOL_LIST_PROJECTS, TOOL_GET_PROJECT, TOOL_DETECT_PROJECT, TOOL_GET_CURRENT_PROJECT,
            TOOL_LIST_ISSUES, TOOL_LIST_MRS, TOOL_GET_MR_NOTES,
            TOOL_LIST_BRANCHES, TOOL_LIST_PIPELINES, TOOL_GET_USER_EVENTS,
            TOOL_LIST_COMMITS, TOOL_LIST_REPOSITORY_TREE, TOOL_LIST_TAGS,
            TOOL_LIST_USER_EVENTS, TOOL_LIST_PROJECT_MEMBERS, TOOL_LIST_PROJECT_HOOKS,
            TOOL_LIST_RELEASES
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
            TOOL_LIST_PROJECTS, TOOL_GET_PROJECT, TOOL_DETECT_PROJECT, TOOL_GET_CURRENT_PROJECT,
            TOOL_LIST_ISSUES, TOOL_LIST_MRS, TOOL_GET_MR_NOTES,
            TOOL_LIST_BRANCHES, TOOL_LIST_PIPELINES, TOOL_GET_USER_EVENTS,
            TOOL_LIST_COMMITS, TOOL_LIST_REPOSITORY_TREE, TOOL_LIST_TAGS,
            TOOL_LIST_USER_EVENTS, TOOL_LIST_PROJECT_MEMBERS, TOOL_LIST_PROJECT_HOOKS,
            TOOL_LIST_RELEASES
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