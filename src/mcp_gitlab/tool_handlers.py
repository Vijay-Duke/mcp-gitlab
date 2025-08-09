"""Tool handlers for MCP GitLab server

This module contains individual handlers for each tool to reduce complexity
in the main server module.
"""
import logging
from typing import Any, Dict, Optional, List
from mcp_gitlab.gitlab_client import GitLabClient
from mcp_gitlab.constants import (
    DEFAULT_PAGE_SIZE, SMALL_PAGE_SIZE, DEFAULT_MAX_BODY_LENGTH,
    ERROR_NO_PROJECT, TOOL_LIST_PROJECTS, TOOL_GET_PROJECT,
    TOOL_GET_CURRENT_PROJECT, TOOL_LIST_ISSUES, TOOL_LIST_MRS,
    TOOL_GET_MR_NOTES, TOOL_LIST_BRANCHES, TOOL_LIST_PIPELINES,
    TOOL_LIST_USER_EVENTS, TOOL_LIST_COMMITS,
    TOOL_LIST_REPOSITORY_TREE, TOOL_LIST_TAGS, TOOL_LIST_RELEASES,
    TOOL_LIST_PROJECT_MEMBERS, TOOL_LIST_PROJECT_HOOKS,
    TOOL_GET_CURRENT_USER, TOOL_GET_USER,
    TOOL_LIST_GROUPS, TOOL_GET_GROUP, TOOL_LIST_GROUP_PROJECTS,
    TOOL_LIST_SNIPPETS, TOOL_GET_SNIPPET, TOOL_CREATE_SNIPPET, TOOL_UPDATE_SNIPPET,
    TOOL_LIST_PIPELINE_JOBS, TOOL_DOWNLOAD_JOB_ARTIFACT, TOOL_LIST_PROJECT_JOBS
)

logger = logging.getLogger(__name__)


def get_argument(arguments: Optional[Dict[str, Any]], key: str, default: Any = None) -> Any:
    """Safely get argument value with default"""
    if arguments is None:
        return default
    return arguments.get(key, default)


def require_argument(arguments: Optional[Dict[str, Any]], key: str, error_msg: Optional[str] = None) -> Any:
    """Get required argument or raise ValueError"""
    if not arguments or key not in arguments:
        raise ValueError(error_msg or f"{key} is required")
    return arguments[key]


def get_project_id_or_detect(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Optional[str]:
    """Get project_id from arguments or detect from git repository"""
    if arguments and arguments.get("project_id"):
        return arguments["project_id"]
    
    detected = client.get_project_from_git(".")
    if detected:
        return detected["id"]
    
    return None


def require_project_id(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> str:
    """Get project_id or raise error if not found"""
    project_id = get_project_id_or_detect(client, arguments)
    if not project_id:
        raise ValueError(ERROR_NO_PROJECT)
    return project_id


# Project Management Handlers
def handle_list_projects(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing projects"""
    owned = get_argument(arguments, "owned", False)
    search = get_argument(arguments, "search")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.get_projects(owned=owned, search=search, per_page=per_page, page=page)


def handle_get_project(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting single project"""
    project_id = require_argument(arguments, "project_id")
    return client.get_project(project_id)


def handle_get_current_project(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting current project using git detection"""
    path = get_argument(arguments, "path", ".")
    result = client.get_current_project(path)

    if not result:
        return {"error": ERROR_NO_PROJECT}
    return result




# Issue Handlers
def handle_list_issues(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing issues"""
    project_id = require_project_id(client, arguments)
    state = get_argument(arguments, "state", "opened")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.get_issues(project_id, state, per_page, page)


def handle_get_issue(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting single issue"""
    project_id = require_project_id(client, arguments)
    issue_iid = require_argument(arguments, "issue_iid")
    
    return client.get_issue(project_id, issue_iid)


# Merge Request Handlers
def handle_list_merge_requests(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing merge requests"""
    project_id = require_project_id(client, arguments)
    state = get_argument(arguments, "state", "opened")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.get_merge_requests(project_id, state, per_page, page)


def handle_get_merge_request(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting single merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    return client.get_merge_request(project_id, mr_iid)


def handle_get_merge_request_notes(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting merge request notes"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    per_page = get_argument(arguments, "per_page", SMALL_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    sort = get_argument(arguments, "sort", "asc")
    order_by = get_argument(arguments, "order_by", "created_at")
    max_body_length = get_argument(arguments, "max_body_length", DEFAULT_MAX_BODY_LENGTH)
    
    return client.get_merge_request_notes(
        project_id, mr_iid, per_page, page, sort, order_by, max_body_length
    )


# Repository File Handlers
def handle_get_file_content(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting file content"""
    project_id = require_project_id(client, arguments)
    file_path = require_argument(arguments, "file_path")
    ref = get_argument(arguments, "ref")
    
    return client.get_file_content(project_id, file_path, ref)


def handle_get_repository_tree(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting repository tree"""
    project_id = require_project_id(client, arguments)
    path = get_argument(arguments, "path", "")
    ref = get_argument(arguments, "ref")
    recursive = get_argument(arguments, "recursive", False)
    
    return client.get_repository_tree(project_id, path, ref, recursive)


# Commit Handlers
def handle_get_commits(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting commits"""
    project_id = require_project_id(client, arguments)
    ref_name = get_argument(arguments, "ref_name")
    since = get_argument(arguments, "since")
    until = get_argument(arguments, "until")
    path = get_argument(arguments, "path")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.get_commits(project_id, ref_name, since, until, path, per_page, page)


def handle_get_commit(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting single commit"""
    project_id = require_project_id(client, arguments)
    commit_sha = require_argument(arguments, "commit_sha")
    include_stats = get_argument(arguments, "include_stats", False)
    
    return client.get_commit(project_id, commit_sha, include_stats)


def handle_get_commit_diff(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting commit diff"""
    project_id = require_project_id(client, arguments)
    commit_sha = require_argument(arguments, "commit_sha")
    
    return client.get_commit_diff(project_id, commit_sha)


# Search Handlers
def handle_search_projects(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle searching projects"""
    search = require_argument(arguments, "search")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.search_projects(search, per_page, page)


def handle_search_in_project(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle searching in project"""
    project_id = require_project_id(client, arguments)
    scope = require_argument(arguments, "scope")
    search = require_argument(arguments, "search")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.search_in_project(project_id, scope, search, per_page, page)


# Repository Info Handlers
def handle_list_branches(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Any:
    """Handle listing branches"""
    project_id = require_project_id(client, arguments)
    return client.get_branches(project_id)


def handle_list_pipelines(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Any:
    """Handle listing pipelines"""
    project_id = require_project_id(client, arguments)
    ref = get_argument(arguments, "ref")
    
    return client.get_pipelines(project_id, ref)


# Authentication & User Handlers
def handle_get_current_user(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting the current authenticated user"""
    return client.get_current_user()


def handle_get_user(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting user details by ID or username"""
    user_id = get_argument(arguments, "user_id")
    username = get_argument(arguments, "username")
    
    if not user_id and not username:
        raise ValueError("Either user_id or username must be provided")
    
    result = client.get_user(user_id=user_id, username=username)
    if result is None:
        raise ValueError(f"User not found: {user_id or username}")
    
    return result


# User Event Handlers
def handle_get_user_events(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting user events"""
    username = require_argument(arguments, "username")
    action = get_argument(arguments, "action")
    target_type = get_argument(arguments, "target_type")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    after = get_argument(arguments, "after")
    before = get_argument(arguments, "before")
    
    return client.get_user_events(username, action, target_type, per_page, page, after, before)


# MR Lifecycle handlers
def handle_update_merge_request(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle updating a merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    # Get all optional update fields
    update_fields = {}
    for field in ['title', 'description', 'assignee_id', 'assignee_ids', 'reviewer_ids', 
                  'labels', 'milestone_id', 'state_event', 'remove_source_branch', 
                  'squash', 'discussion_locked', 'allow_collaboration', 'target_branch']:
        if arguments and field in arguments:
            update_fields[field] = arguments[field]
    
    return client.update_merge_request(project_id, mr_iid, **update_fields)


def handle_close_merge_request(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle closing a merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    return client.close_merge_request(project_id, mr_iid)


def handle_merge_merge_request(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle merging a merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    merge_when_pipeline_succeeds = get_argument(arguments, "merge_when_pipeline_succeeds", False)
    should_remove_source_branch = get_argument(arguments, "should_remove_source_branch")
    merge_commit_message = get_argument(arguments, "merge_commit_message")
    squash_commit_message = get_argument(arguments, "squash_commit_message")
    squash = get_argument(arguments, "squash")
    
    return client.merge_merge_request(project_id, mr_iid, merge_when_pipeline_succeeds,
                                    should_remove_source_branch, merge_commit_message,
                                    squash_commit_message, squash)


# Comment handlers
def handle_add_issue_comment(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle adding a comment to an issue"""
    project_id = require_project_id(client, arguments)
    issue_iid = require_argument(arguments, "issue_iid")
    body = require_argument(arguments, "body")
    
    return client.add_issue_comment(project_id, issue_iid, body)


def handle_add_merge_request_comment(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle adding a comment to a merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    body = require_argument(arguments, "body")
    
    return client.add_merge_request_comment(project_id, mr_iid, body)


# Approval handlers
def handle_approve_merge_request(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle approving a merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    return client.approve_merge_request(project_id, mr_iid)


def handle_get_merge_request_approvals(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting merge request approvals"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    return client.get_merge_request_approvals(project_id, mr_iid)


# Repository handlers
def handle_get_tags(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Handle getting project tags"""
    project_id = require_project_id(client, arguments)
    order_by = get_argument(arguments, "order_by", "updated")
    sort = get_argument(arguments, "sort", "desc")
    
    return client.get_tags(project_id, order_by, sort)


def handle_create_commit(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle creating a commit with multiple file changes"""
    project_id = require_project_id(client, arguments)
    branch = require_argument(arguments, "branch")
    commit_message = require_argument(arguments, "commit_message")
    actions = require_argument(arguments, "actions")
    
    author_email = get_argument(arguments, "author_email")
    author_name = get_argument(arguments, "author_name")
    
    return client.create_commit(project_id, branch, commit_message, actions, author_email, author_name)


def handle_compare_refs(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle comparing two refs"""
    project_id = require_project_id(client, arguments)
    from_ref = require_argument(arguments, "from_ref")
    to_ref = require_argument(arguments, "to_ref")
    straight = get_argument(arguments, "straight", False)
    
    return client.compare_refs(project_id, from_ref, to_ref, straight)


# Release and member handlers
def handle_list_releases(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing project releases"""
    project_id = require_project_id(client, arguments)
    order_by = get_argument(arguments, "order_by", "released_at")
    sort = get_argument(arguments, "sort", "desc")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.list_releases(project_id, order_by, sort, per_page, page)


def handle_get_project_members(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting project members"""
    project_id = require_project_id(client, arguments)
    query = get_argument(arguments, "query")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.get_project_members(project_id, query, per_page, page)


def handle_get_project_hooks(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Handle getting project webhooks"""
    project_id = require_project_id(client, arguments)
    
    return client.get_project_hooks(project_id)


# MR advanced handlers
def handle_get_merge_request_discussions(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting merge request discussions"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.get_merge_request_discussions(project_id, mr_iid, per_page, page)


def handle_resolve_discussion(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle resolving a discussion"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    discussion_id = require_argument(arguments, "discussion_id")
    
    return client.resolve_discussion(project_id, mr_iid, discussion_id)


def handle_get_merge_request_changes(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting merge request changes"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    return client.get_merge_request_changes(project_id, mr_iid)


# MR operations handlers
def handle_rebase_merge_request(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle rebasing a merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    
    return client.rebase_merge_request(project_id, mr_iid)


def handle_cherry_pick_commit(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle cherry-picking a commit"""
    project_id = require_project_id(client, arguments)
    commit_sha = require_argument(arguments, "commit_sha")
    branch = require_argument(arguments, "branch")
    
    return client.cherry_pick_commit(project_id, commit_sha, branch)


# AI helper handlers
def handle_summarize_merge_request(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle summarizing a merge request"""
    project_id = require_project_id(client, arguments)
    mr_iid = require_argument(arguments, "mr_iid")
    max_length = get_argument(arguments, "max_length", 500)
    
    return client.summarize_merge_request(project_id, mr_iid, max_length)


def handle_summarize_issue(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle summarizing an issue"""
    project_id = require_project_id(client, arguments)
    issue_iid = require_argument(arguments, "issue_iid")
    max_length = get_argument(arguments, "max_length", 500)
    
    return client.summarize_issue(project_id, issue_iid, max_length)


def handle_summarize_pipeline(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle summarizing a pipeline"""
    project_id = require_project_id(client, arguments)
    pipeline_id = require_argument(arguments, "pipeline_id")
    max_length = get_argument(arguments, "max_length", 500)
    
    return client.summarize_pipeline(project_id, pipeline_id, max_length)


# Advanced diff handlers
def handle_smart_diff(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting a smart diff between refs"""
    project_id = require_project_id(client, arguments)
    from_ref = require_argument(arguments, "from_ref")
    to_ref = require_argument(arguments, "to_ref")
    context_lines = get_argument(arguments, "context_lines", 3)
    max_file_size = get_argument(arguments, "max_file_size", 50000)
    
    return client.smart_diff(project_id, from_ref, to_ref, context_lines, max_file_size)


def handle_safe_preview_commit(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle previewing a commit"""
    project_id = require_project_id(client, arguments)
    branch = require_argument(arguments, "branch")
    commit_message = require_argument(arguments, "commit_message")
    actions = require_argument(arguments, "actions")
    
    return client.safe_preview_commit(project_id, branch, commit_message, actions)


# Batch operations handler
def handle_batch_operations(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle batch operations"""
    project_id = require_project_id(client, arguments)
    operations = require_argument(arguments, "operations")
    stop_on_error = get_argument(arguments, "stop_on_error", True)
    
    return client.batch_operations(project_id, operations, stop_on_error)


# Snippets handlers
def handle_list_snippets(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing project snippets"""
    project_id = require_project_id(client, arguments)
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.list_snippets(project_id, per_page=per_page, page=page)


def handle_get_snippet(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting single snippet"""
    project_id = require_project_id(client, arguments)
    snippet_id = require_argument(arguments, "snippet_id")
    
    return client.get_snippet(project_id, snippet_id)


def handle_create_snippet(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle creating a snippet"""
    project_id = require_project_id(client, arguments)
    title = require_argument(arguments, "title")
    file_name = require_argument(arguments, "file_name")
    content = require_argument(arguments, "content")
    description = get_argument(arguments, "description")
    visibility = get_argument(arguments, "visibility", "private")
    
    return client.create_snippet(
        project_id=project_id,
        title=title,
        file_name=file_name,
        content=content,
        description=description,
        visibility=visibility
    )


def handle_update_snippet(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle updating a snippet"""
    project_id = require_project_id(client, arguments)
    snippet_id = require_argument(arguments, "snippet_id")
    title = get_argument(arguments, "title")
    file_name = get_argument(arguments, "file_name")
    content = get_argument(arguments, "content")
    description = get_argument(arguments, "description")
    visibility = get_argument(arguments, "visibility")
    
    return client.update_snippet(
        project_id=project_id,
        snippet_id=snippet_id,
        title=title,
        file_name=file_name,
        content=content,
        description=description,
        visibility=visibility
    )


# Group handlers
def handle_list_groups(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing groups"""
    search = get_argument(arguments, "search")
    owned = get_argument(arguments, "owned", False)
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.list_groups(search=search, owned=owned, per_page=per_page, page=page)


def handle_get_group(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle getting single group"""
    group_id = require_argument(arguments, "group_id")
    with_projects = get_argument(arguments, "with_projects", False)
    
    return client.get_group(group_id, with_projects=with_projects)


def handle_list_group_projects(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing projects within a group"""
    group_id = require_argument(arguments, "group_id")
    search = get_argument(arguments, "search")
    include_subgroups = get_argument(arguments, "include_subgroups", False)
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.list_group_projects(
        group_id, 
        search=search, 
        include_subgroups=include_subgroups,
        per_page=per_page, 
        page=page
    )


# Job and Artifact handlers
def handle_list_pipeline_jobs(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing jobs in a pipeline"""
    project_id = require_project_id(client, arguments)
    pipeline_id = require_argument(arguments, "pipeline_id")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.list_pipeline_jobs(project_id, pipeline_id, per_page=per_page, page=page)


def handle_download_job_artifact(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle downloading job artifacts"""
    project_id = require_project_id(client, arguments)
    job_id = require_argument(arguments, "job_id")
    artifact_path = get_argument(arguments, "artifact_path")
    
    return client.download_job_artifact(project_id, job_id, artifact_path)


def handle_list_project_jobs(client: GitLabClient, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Handle listing jobs for a project"""
    project_id = require_project_id(client, arguments)
    scope = get_argument(arguments, "scope")
    per_page = get_argument(arguments, "per_page", DEFAULT_PAGE_SIZE)
    page = get_argument(arguments, "page", 1)
    
    return client.list_project_jobs(project_id, scope=scope, per_page=per_page, page=page)

# Tool handler mapping
TOOL_HANDLERS = {
    TOOL_LIST_PROJECTS: handle_list_projects,
    TOOL_GET_PROJECT: handle_get_project,
    TOOL_GET_CURRENT_PROJECT: handle_get_current_project,
    TOOL_GET_CURRENT_USER: handle_get_current_user,
    TOOL_GET_USER: handle_get_user,
    TOOL_LIST_ISSUES: handle_list_issues,
    "gitlab_get_issue": handle_get_issue,
    TOOL_LIST_MRS: handle_list_merge_requests,
    "gitlab_get_merge_request": handle_get_merge_request,
    TOOL_GET_MR_NOTES: handle_get_merge_request_notes,
    "gitlab_get_file_content": handle_get_file_content,
    TOOL_LIST_REPOSITORY_TREE: handle_get_repository_tree,
    TOOL_LIST_COMMITS: handle_get_commits,  # Same handler, new name
    "gitlab_get_commit": handle_get_commit,
    "gitlab_get_commit_diff": handle_get_commit_diff,
    "gitlab_search_projects": handle_search_projects,
    "gitlab_search_in_project": handle_search_in_project,
    TOOL_LIST_BRANCHES: handle_list_branches,
    TOOL_LIST_PIPELINES: handle_list_pipelines,
    TOOL_LIST_USER_EVENTS: handle_get_user_events,
    
    # MR lifecycle handlers
    "gitlab_update_merge_request": handle_update_merge_request,
    "gitlab_close_merge_request": handle_close_merge_request,
    "gitlab_merge_merge_request": handle_merge_merge_request,
    
    # Comment handlers
    "gitlab_add_issue_comment": handle_add_issue_comment,
    "gitlab_add_merge_request_comment": handle_add_merge_request_comment,
    
    # Approval handlers
    "gitlab_approve_merge_request": handle_approve_merge_request,
    "gitlab_get_merge_request_approvals": handle_get_merge_request_approvals,
    
    # Repository handlers
    TOOL_LIST_TAGS: handle_get_tags,  # Same handler, new name
    "gitlab_create_commit": handle_create_commit,
    "gitlab_compare_refs": handle_compare_refs,
    
    # Release and member handlers
    "gitlab_list_releases": handle_list_releases,
    TOOL_LIST_RELEASES: handle_list_releases,  # Same handler, new name
    TOOL_LIST_PROJECT_MEMBERS: handle_get_project_members,  # Same handler, new name
    TOOL_LIST_PROJECT_HOOKS: handle_get_project_hooks,  # Same handler, new name
    
    # MR advanced handlers
    "gitlab_get_merge_request_discussions": handle_get_merge_request_discussions,
    "gitlab_resolve_discussion": handle_resolve_discussion,
    "gitlab_get_merge_request_changes": handle_get_merge_request_changes,
    
    # MR operations handlers
    "gitlab_rebase_merge_request": handle_rebase_merge_request,
    "gitlab_cherry_pick_commit": handle_cherry_pick_commit,
    
    # AI helper handlers
    "gitlab_summarize_merge_request": handle_summarize_merge_request,
    "gitlab_summarize_issue": handle_summarize_issue,
    "gitlab_summarize_pipeline": handle_summarize_pipeline,
    
    # Advanced diff handlers
    "gitlab_smart_diff": handle_smart_diff,
    "gitlab_safe_preview_commit": handle_safe_preview_commit,
    
    # Batch operations handler
    "gitlab_batch_operations": handle_batch_operations,
    
    # Group handlers
    TOOL_LIST_GROUPS: handle_list_groups,
    TOOL_GET_GROUP: handle_get_group,
    TOOL_LIST_GROUP_PROJECTS: handle_list_group_projects,
    
    # Snippets handlers
    TOOL_LIST_SNIPPETS: handle_list_snippets,
    TOOL_GET_SNIPPET: handle_get_snippet,
    TOOL_CREATE_SNIPPET: handle_create_snippet,
    TOOL_UPDATE_SNIPPET: handle_update_snippet,
    
    # Job and Artifact handlers
    TOOL_LIST_PIPELINE_JOBS: handle_list_pipeline_jobs,
    TOOL_DOWNLOAD_JOB_ARTIFACT: handle_download_job_artifact,
    TOOL_LIST_PROJECT_JOBS: handle_list_project_jobs,
}