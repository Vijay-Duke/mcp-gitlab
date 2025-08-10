"""
Tool definitions for the MCP GitLab server.

This module contains the list of all tool definitions provided by the server.
It is separated from server.py to improve readability and maintainability.
"""
from typing import List

try:
    import mcp.types as types
except ImportError:
    # This is a mock for environments where mcp is not installed.
    # The server itself will fail to start if mcp is truly missing.
    class MockType:
        def __init__(self, *args, **kwargs):
            pass
    class MockTypes:
        Tool = MockType
    types = MockTypes()

from . import tool_descriptions as desc
from .constants import *


TOOLS: List[types.Tool] = [
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
        name=TOOL_GET_ISSUE,
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
        name=TOOL_GET_MERGE_REQUEST,
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
        name=TOOL_GET_FILE_CONTENT,
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
        name=TOOL_GET_COMMIT,
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
        name=TOOL_GET_COMMIT_DIFF,
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
        name=TOOL_SEARCH_PROJECTS,
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
        name=TOOL_SEARCH_IN_PROJECT,
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
        name=TOOL_UPDATE_MR,
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
        name=TOOL_CLOSE_MR,
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
        name=TOOL_MERGE_MR,
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
        name=TOOL_ADD_ISSUE_COMMENT,
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
        name=TOOL_ADD_MR_COMMENT,
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
        name=TOOL_APPROVE_MR,
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
        name=TOOL_GET_MR_APPROVALS,
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
        name=TOOL_CREATE_COMMIT,
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
        name=TOOL_COMPARE_REFS,
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
        name=TOOL_GET_MR_DISCUSSIONS,
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
        name=TOOL_RESOLVE_DISCUSSION,
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
        name=TOOL_GET_MR_CHANGES,
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
        name=TOOL_REBASE_MR,
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
        name=TOOL_CHERRY_PICK_COMMIT,
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
        name=TOOL_SUMMARIZE_MR,
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
        name=TOOL_SUMMARIZE_ISSUE,
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
        name=TOOL_SUMMARIZE_PIPELINE,
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
        name=TOOL_SMART_DIFF,
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
        name=TOOL_SAFE_PREVIEW_COMMIT,
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
        name=TOOL_BATCH_OPERATIONS,
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
    )
]
