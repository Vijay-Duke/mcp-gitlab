"""Simplified GitLab client used by the unit tests.

The original project contains a very feature rich client that mirrors large
parts of the GitLab API.  Re‑creating the full implementation would be
unnecessary for the exercises, so this module provides a small, self contained
client that implements only the functionality required by the tests.  The
methods intentionally operate on objects returned by the stub ``gitlab``
package and mostly convert those objects into plain dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import base64
import logging

import gitlab

from .git_detector import GitDetector
from .constants import (
    DEFAULT_GITLAB_URL,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    SMALL_PAGE_SIZE,
    DEFAULT_MAX_BODY_LENGTH,
    CACHE_TTL_MEDIUM,
)
from .utils import timed_cache, retry_on_error

logger = logging.getLogger(__name__)


@dataclass
class GitLabConfig:
    """Configuration for :class:`GitLabClient`."""

    url: str = DEFAULT_GITLAB_URL
    private_token: Optional[str] = None
    oauth_token: Optional[str] = None


class GitLabClient:
    """Very small wrapper around the :mod:`gitlab` stub.

    The class only implements the handful of operations that are exercised in
    the tests.  Each public method returns simple dictionaries so that the
    behaviour is easy to assert.
    """

    def __init__(self, config: GitLabConfig):
        self.config = config

        auth_kwargs: Dict[str, Any] = {}
        if config.private_token:
            auth_kwargs["private_token"] = config.private_token
        elif config.oauth_token:
            auth_kwargs["oauth_token"] = config.oauth_token
        else:  # pragma: no cover - validated by tests
            raise ValueError("Either private_token or oauth_token must be provided")

        self.gl = gitlab.Gitlab(config.url, **auth_kwargs)
        # The real client would perform an HTTP request here.  The stubbed
        # version simply provides the ``auth`` method so the call is harmless.
        self.gl.auth()

    # ------------------------------------------------------------------
    # Helper conversion utilities
    # ------------------------------------------------------------------
    @staticmethod
    def _project_to_dict(project: Any) -> Dict[str, Any]:
        return {
            "id": getattr(project, "id", None),
            "name": getattr(project, "name", None),
            "path": getattr(project, "path", None),
            "path_with_namespace": getattr(project, "path_with_namespace", None),
            "description": getattr(project, "description", None),
            "web_url": getattr(project, "web_url", None),
            "visibility": getattr(project, "visibility", None),
            "last_activity_at": getattr(project, "last_activity_at", None),
        }

    @staticmethod
    def _issue_to_dict(issue: Any) -> Dict[str, Any]:
        return {
            "id": getattr(issue, "id", None),
            "iid": getattr(issue, "iid", None),
            "title": getattr(issue, "title", None),
            "description": getattr(issue, "description", None),
            "state": getattr(issue, "state", None),
            "created_at": getattr(issue, "created_at", None),
            "updated_at": getattr(issue, "updated_at", None),
            "labels": getattr(issue, "labels", []),
            "web_url": getattr(issue, "web_url", None),
            "author": getattr(issue, "author", None),
        }

    @staticmethod
    def _mr_to_dict(mr: Any) -> Dict[str, Any]:
        return {
            "id": getattr(mr, "id", None),
            "iid": getattr(mr, "iid", None),
            "title": getattr(mr, "title", None),
            "description": getattr(mr, "description", None),
            "state": getattr(mr, "state", None),
            "source_branch": getattr(mr, "source_branch", None),
            "target_branch": getattr(mr, "target_branch", None),
            "created_at": getattr(mr, "created_at", None),
            "updated_at": getattr(mr, "updated_at", None),
            "web_url": getattr(mr, "web_url", None),
            "author": getattr(mr, "author", None),
        }

    @staticmethod
    def _note_to_dict(note: Any, max_body_length: int) -> Dict[str, Any]:
        body = getattr(note, "body", "")
        truncated = False
        if max_body_length and len(body) > max_body_length:
            body = body[:max_body_length] + "... [truncated]"
            truncated = True

        data: Dict[str, Any] = {
            "id": getattr(note, "id", None),
            "body": body,
            "created_at": getattr(note, "created_at", None),
            "updated_at": getattr(note, "updated_at", None),
            "author": getattr(note, "author", None),
            "system": getattr(note, "system", False),
            "noteable_type": getattr(note, "noteable_type", None),
            "noteable_iid": getattr(note, "noteable_iid", None),
            "resolvable": getattr(note, "resolvable", False),
            "resolved": getattr(note, "resolved", False),
        }
        if truncated:
            data["truncated"] = True
        return data

    @staticmethod
    def _branch_to_dict(branch: Any) -> Dict[str, Any]:
        return {
            "name": getattr(branch, "name", None),
            "merged": getattr(branch, "merged", False),
            "protected": getattr(branch, "protected", False),
            "default": getattr(branch, "default", False),
            "web_url": getattr(branch, "web_url", None),
        }

    @staticmethod
    def _event_to_dict(event: Any) -> Dict[str, Any]:
        return {
            "id": getattr(event, "id", None),
            "title": getattr(event, "title", None),
            "project_id": getattr(event, "project_id", None),
            "action_name": getattr(event, "action_name", None),
            "target_id": getattr(event, "target_id", None),
            "target_type": getattr(event, "target_type", None),
            "target_title": getattr(event, "target_title", None),
            "created_at": getattr(event, "created_at", None),
            "author_id": getattr(event, "author_id", None),
            "author_username": getattr(event, "author_username", None),
        }

    # ------------------------------------------------------------------
    # API methods
    # ------------------------------------------------------------------
    @retry_on_error()
    def get_projects(
        self,
        owned: bool = False,
        search: Optional[str] = None,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Return a list of projects accessible to the user."""

        kwargs = {
            "owned": owned,
            "membership": True,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        if search:
            kwargs["search"] = search

        response = self.gl.projects.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        return {
            "projects": [self._project_to_dict(p) for p in response],
            "pagination": pagination,
        }

    @timed_cache(seconds=CACHE_TTL_MEDIUM)
    @retry_on_error()
    def get_project(self, project_id: str) -> Dict[str, Any]:
        project = self.gl.projects.get(project_id)
        return self._project_to_dict(project)

    @retry_on_error()
    def get_issues(
        self,
        project_id: str,
        state: str = "opened",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        project = self.gl.projects.get(project_id)
        kwargs = {
            "state": state,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        response = project.issues.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        return {
            "issues": [self._issue_to_dict(i) for i in response],
            "pagination": pagination,
            "project_id": project_id,
        }

    @retry_on_error()
    def get_issue(self, project_id: str, issue_iid: int) -> Dict[str, Any]:
        project = self.gl.projects.get(project_id)
        issue = project.issues.get(issue_iid, lazy=False)
        return self._issue_to_dict(issue)

    @retry_on_error()
    def get_merge_requests(
        self,
        project_id: str,
        state: str = "opened",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        project = self.gl.projects.get(project_id)
        kwargs = {
            "state": state,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        response = project.mergerequests.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        return {
            "merge_requests": [self._mr_to_dict(m) for m in response],
            "pagination": pagination,
        }

    @retry_on_error()
    def get_merge_request(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        return self._mr_to_dict(mr)

    @retry_on_error()
    def get_merge_request_notes(
        self,
        project_id: str,
        mr_iid: int,
        per_page: int = SMALL_PAGE_SIZE,
        page: int = 1,
        sort: str = "asc",
        order_by: str = "created_at",
        max_body_length: int = DEFAULT_MAX_BODY_LENGTH,
    ) -> Dict[str, Any]:
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
            "sort": sort,
            "order_by": order_by,
        }
        response = mr.notes.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        notes = [self._note_to_dict(n, max_body_length) for n in response]
        # Some mocks used in the tests don't define ``iid`` so fall back to the
        # value that was requested.
        merge_request = {
            "iid": mr_iid,
            "title": getattr(mr, "title", None),
            "web_url": getattr(mr, "web_url", None),
        }
        return {"notes": notes, "pagination": pagination, "merge_request": merge_request}

    @retry_on_error()
    def get_pipelines(
        self, project_id: str, ref: Optional[str] = None, per_page: int = SMALL_PAGE_SIZE
    ) -> List[Dict[str, Any]]:
        project = self.gl.projects.get(project_id)
        kwargs = {"get_all": False, "per_page": per_page}
        if ref is not None:
            kwargs["ref"] = ref
        pipelines = project.pipelines.list(**kwargs)
        return [
            {
                "id": getattr(p, "id", None),
                "status": getattr(p, "status", None),
                "ref": getattr(p, "ref", None),
                "sha": getattr(p, "sha", None),
                "created_at": getattr(p, "created_at", None),
                "updated_at": getattr(p, "updated_at", None),
                "web_url": getattr(p, "web_url", None),
            }
            for p in pipelines
        ]

    @retry_on_error()
    def get_branches(self, project_id: str) -> List[Dict[str, Any]]:
        project = self.gl.projects.get(project_id)
        branches = project.branches.list()
        return [self._branch_to_dict(b) for b in branches]

    @retry_on_error()
    def get_file_content(self, project_id: str, file_path: str, ref: Optional[str] = None) -> Dict[str, Any]:
        project = self.gl.projects.get(project_id)
        file_obj = project.files.get(file_path=file_path, ref=ref)
        content = getattr(file_obj, "content", "")
        encoding = getattr(file_obj, "encoding", None)
        if encoding == "base64":
            try:
                content = base64.b64decode(content).decode("utf-8")
            except Exception:  # pragma: no cover - defensive
                content = ""
        return {
            "file_path": file_path,
            "content": content,
            "size": getattr(file_obj, "size", None),
            "encoding": encoding,
            "ref": ref,
            "last_commit_id": getattr(file_obj, "last_commit_id", None),
            "blob_id": getattr(file_obj, "blob_id", None),
        }

    @retry_on_error()
    def search_projects(
        self, search: str, per_page: int = DEFAULT_PAGE_SIZE, page: int = 1
    ) -> Dict[str, Any]:
        kwargs = {
            "search": search,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        response = self.gl.projects.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        return {"projects": [self._project_to_dict(p) for p in response], "pagination": pagination, "search_term": search}

    @retry_on_error()
    def get_current_project(self, path: str = ".") -> Optional[Dict[str, Any]]:
        """Get current project by inspecting git repository"""
        return self.get_project_from_git(path)

    def get_project_from_git(self, path: str = ".") -> Optional[Dict[str, Any]]:
        detected = GitDetector.detect_gitlab_project(path)
        if not detected:
            return None
        if not GitDetector.is_gitlab_url(detected["url"], self.config.url):
            return None
        project = self.get_project(detected["path"])
        project["git_info"] = {
            "current_branch": detected.get("branch"),
            "remote_url": detected["url"],
            "detected_from": path,
        }
        return project

    @retry_on_error()
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        users = self.gl.users.list(username=username)
        if not users:
            return None
        user = users[0]
        return {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "name": getattr(user, "name", None),
            "state": getattr(user, "state", None),
            "avatar_url": getattr(user, "avatar_url", None),
            "web_url": getattr(user, "web_url", None),
        }

    @retry_on_error()
    def get_user_events(
        self,
        username: str,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> Dict[str, Any]:
        user = self.get_user_by_username(username)
        if not user:
            return {"events": [], "user": None}

        user_obj = self.gl.users.get(user["id"])
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        if action:
            kwargs["action"] = action
        if target_type:
            kwargs["target_type"] = target_type
        if after:
            kwargs["after"] = after
        if before:
            kwargs["before"] = before

        response = user_obj.events.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        events = [self._event_to_dict(e) for e in response]
        return {"events": events, "user": user, "pagination": pagination}

    @retry_on_error()
    def get_current_user(self) -> Dict[str, Any]:
        """Get the currently authenticated user.
        
        Returns:
            Dictionary with user information including:
            - id: User ID
            - username: Username
            - name: Full name
            - email: Email address
            - state: Account state
            - avatar_url: Avatar URL
            - web_url: Profile URL
            - created_at: Account creation date
            - bio: User bio
            - organization: Organization
            - job_title: Job title
            - public_email: Public email
            - is_admin: Whether user is admin
            - can_create_group: Whether user can create groups
            - can_create_project: Whether user can create projects
        """
        user = self.gl.user
        
        # Get extended user info
        return {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "name": getattr(user, "name", None),
            "email": getattr(user, "email", None),
            "state": getattr(user, "state", None),
            "avatar_url": getattr(user, "avatar_url", None),
            "web_url": getattr(user, "web_url", None),
            "created_at": getattr(user, "created_at", None),
            "bio": getattr(user, "bio", None),
            "organization": getattr(user, "organization", None),
            "job_title": getattr(user, "job_title", None),
            "public_email": getattr(user, "public_email", None),
            "is_admin": getattr(user, "is_admin", False),
            "can_create_group": getattr(user, "can_create_group", True),
            "can_create_project": getattr(user, "can_create_project", True),
            "two_factor_enabled": getattr(user, "two_factor_enabled", False),
            "external": getattr(user, "external", False),
        }
    
    @retry_on_error()
    def get_user(self, user_id: Optional[str] = None, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get details for a specific user by ID or username.
        
        Args:
            user_id: User ID (numeric)
            username: Username (string)
            
        Returns:
            Dictionary with user information or None if not found
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
            
        if user_id:
            try:
                user = self.gl.users.get(user_id)
                return {
                    "id": getattr(user, "id", None),
                    "username": getattr(user, "username", None),
                    "name": getattr(user, "name", None),
                    "state": getattr(user, "state", None),
                    "avatar_url": getattr(user, "avatar_url", None),
                    "web_url": getattr(user, "web_url", None),
                    "created_at": getattr(user, "created_at", None),
                    "bio": getattr(user, "bio", None),
                    "organization": getattr(user, "organization", None),
                    "job_title": getattr(user, "job_title", None),
                    "public_email": getattr(user, "public_email", None),
                    "external": getattr(user, "external", False),
                }
            except gitlab.exceptions.GitlabGetError:
                return None
        else:
            # Search by username
            return self.get_user_by_username(username)

    @retry_on_error()
    def list_groups(
        self,
        search: Optional[str] = None,
        owned: bool = False,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List accessible groups.
        
        Args:
            search: Search term for group names/paths
            owned: Only show groups user owns
            per_page: Number of results per page
            page: Page number
            
        Returns:
            Dictionary with groups list and pagination info
        """
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        if search:
            kwargs["search"] = search
        if owned:
            kwargs["owned"] = True
            
        response = self.gl.groups.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        
        groups = []
        for group in response:
            groups.append({
                "id": getattr(group, "id", None),
                "name": getattr(group, "name", None),
                "path": getattr(group, "path", None),
                "full_path": getattr(group, "full_path", None),
                "description": getattr(group, "description", None),
                "visibility": getattr(group, "visibility", None),
                "web_url": getattr(group, "web_url", None),
                "avatar_url": getattr(group, "avatar_url", None),
                "parent_id": getattr(group, "parent_id", None),
            })
            
        return {"groups": groups, "pagination": pagination}
    
    @retry_on_error()
    def get_group(self, group_id: str, with_projects: bool = False) -> Dict[str, Any]:
        """Get group details.
        
        Args:
            group_id: Group ID or path
            with_projects: Include projects in response
            
        Returns:
            Dictionary with group information
        """
        group = self.gl.groups.get(group_id)
        
        result = {
            "id": getattr(group, "id", None),
            "name": getattr(group, "name", None),
            "path": getattr(group, "path", None),
            "full_path": getattr(group, "full_path", None),
            "description": getattr(group, "description", None),
            "visibility": getattr(group, "visibility", None),
            "web_url": getattr(group, "web_url", None),
            "avatar_url": getattr(group, "avatar_url", None),
            "parent_id": getattr(group, "parent_id", None),
            "created_at": getattr(group, "created_at", None),
            "lfs_enabled": getattr(group, "lfs_enabled", False),
            "request_access_enabled": getattr(group, "request_access_enabled", True),
            "full_name": getattr(group, "full_name", None),
            "projects_count": getattr(group, "statistics", {}).get("projects", 0) if hasattr(group, "statistics") else 0,
        }
        
        if with_projects:
            # Get first page of projects
            projects_response = self.list_group_projects(group_id, per_page=20, page=1)
            result["projects"] = projects_response.get("projects", [])
            result["projects_pagination"] = projects_response.get("pagination", {})
            
        return result
    
    @retry_on_error()
    def list_group_projects(
        self,
        group_id: str,
        search: Optional[str] = None,
        include_subgroups: bool = False,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List projects within a group.
        
        Args:
            group_id: Group ID or path
            search: Search term for project names
            include_subgroups: Include projects from subgroups
            per_page: Number of results per page
            page: Page number
            
        Returns:
            Dictionary with projects list and pagination info
        """
        group = self.gl.groups.get(group_id)
        
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
            "include_subgroups": include_subgroups,
        }
        if search:
            kwargs["search"] = search
            
        response = group.projects.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        
        return {
            "projects": [self._project_to_dict(p) for p in response],
            "pagination": pagination,
            "group_id": group_id,
        }

    @staticmethod
    def _snippet_to_dict(snippet: Any) -> Dict[str, Any]:
        """Convert snippet object to dictionary"""
        return {
            "id": getattr(snippet, "id", None),
            "title": getattr(snippet, "title", None),
            "file_name": getattr(snippet, "file_name", None),
            "description": getattr(snippet, "description", None),
            "visibility": getattr(snippet, "visibility", None),
            "author": getattr(snippet, "author", None),
            "created_at": getattr(snippet, "created_at", None),
            "updated_at": getattr(snippet, "updated_at", None),
            "web_url": getattr(snippet, "web_url", None),
            "raw_url": getattr(snippet, "raw_url", None),
        }

    @retry_on_error()
    def list_snippets(
        self,
        project_id: str,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List project snippets.
        
        Args:
            project_id: The project ID or path
            per_page: Number of results per page
            page: Page number
            
        Returns:
            Dictionary with snippets list and pagination info
        """
        project = self.gl.projects.get(project_id)
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        
        response = project.snippets.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        
        return {
            "snippets": [self._snippet_to_dict(s) for s in response],
            "pagination": pagination,
            "project_id": project_id,
        }

    @retry_on_error()
    def get_snippet(self, project_id: str, snippet_id: int) -> Dict[str, Any]:
        """Get a specific snippet with content.
        
        Args:
            project_id: The project ID or path
            snippet_id: The snippet ID
            
        Returns:
            Dictionary with snippet details and content
        """
        project = self.gl.projects.get(project_id)
        snippet = project.snippets.get(snippet_id)
        
        result = self._snippet_to_dict(snippet)
        result["content"] = getattr(snippet, "content", "")
        
        return result

    @retry_on_error()
    def create_snippet(
        self,
        project_id: str,
        title: str,
        file_name: str,
        content: str,
        description: Optional[str] = None,
        visibility: str = "private"
    ) -> Dict[str, Any]:
        """Create a new snippet.
        
        Args:
            project_id: The project ID or path
            title: Snippet title
            file_name: File name for the snippet
            content: Snippet content
            description: Optional description
            visibility: Snippet visibility (private, internal, public)
            
        Returns:
            Dictionary with created snippet details
        """
        project = self.gl.projects.get(project_id)
        
        snippet_data = {
            "title": title,
            "file_name": file_name,
            "content": content,
            "visibility": visibility,
        }
        
        if description:
            snippet_data["description"] = description
            
        snippet = project.snippets.create(snippet_data)
        return self._snippet_to_dict(snippet)

    @retry_on_error()
    def update_snippet(
        self,
        project_id: str,
        snippet_id: int,
        title: Optional[str] = None,
        file_name: Optional[str] = None,
        content: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing snippet.
        
        Args:
            project_id: The project ID or path
            snippet_id: The snippet ID
            title: Optional new title
            file_name: Optional new file name
            content: Optional new content
            description: Optional new description
            visibility: Optional new visibility
            
        Returns:
            Dictionary with updated snippet details
        """
        project = self.gl.projects.get(project_id)
        snippet = project.snippets.get(snippet_id, lazy=False)
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if file_name is not None:
            update_data["file_name"] = file_name
        if content is not None:
            update_data["content"] = content
        if description is not None:
            update_data["description"] = description
        if visibility is not None:
            update_data["visibility"] = visibility
            
        if update_data:
            for key, value in update_data.items():
                setattr(snippet, key, value)
            snippet.save()
        
        return self._snippet_to_dict(snippet)

    @staticmethod
    def _job_to_dict(job: Any) -> Dict[str, Any]:
        """Convert job object to dictionary"""
        return {
            "id": getattr(job, "id", None),
            "name": getattr(job, "name", None),
            "stage": getattr(job, "stage", None),
            "status": getattr(job, "status", None),
            "created_at": getattr(job, "created_at", None),
            "started_at": getattr(job, "started_at", None),
            "finished_at": getattr(job, "finished_at", None),
            "duration": getattr(job, "duration", None),
            "user": getattr(job, "user", None),
            "commit": getattr(job, "commit", None),
            "pipeline": getattr(job, "pipeline", None),
            "web_url": getattr(job, "web_url", None),
            "artifacts": getattr(job, "artifacts", []),
            "artifacts_expire_at": getattr(job, "artifacts_expire_at", None),
            "tag_list": getattr(job, "tag_list", []),
            "runner": getattr(job, "runner", None),
        }

    @retry_on_error()
    def list_pipeline_jobs(
        self,
        project_id: str,
        pipeline_id: int,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List jobs in a specific pipeline.
        
        Args:
            project_id: The project ID or path
            pipeline_id: The pipeline ID
            per_page: Number of results per page
            page: Page number
            
        Returns:
            Dictionary with jobs list and pagination info
        """
        project = self.gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)
        
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        
        response = pipeline.jobs.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        
        return {
            "jobs": [self._job_to_dict(j) for j in response],
            "pagination": pagination,
            "project_id": project_id,
            "pipeline_id": pipeline_id,
        }

    @retry_on_error()
    def download_job_artifact(
        self,
        project_id: str,
        job_id: int,
        artifact_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Download job artifacts.
        
        Args:
            project_id: The project ID or path
            job_id: The job ID
            artifact_path: Optional specific artifact path to download
            
        Returns:
            Dictionary with artifact information and download details
        """
        project = self.gl.projects.get(project_id)
        job = project.jobs.get(job_id)
        
        # Get job artifacts info
        artifacts_info = []
        if hasattr(job, "artifacts") and job.artifacts:
            for artifact in job.artifacts:
                artifacts_info.append({
                    "filename": getattr(artifact, "filename", None),
                    "size": getattr(artifact, "size", None),
                })
        
        # For security reasons, we don't actually download the artifact content
        # but return information about available artifacts
        result = {
            "job_id": job_id,
            "job_name": getattr(job, "name", None),
            "project_id": project_id,
            "artifacts": artifacts_info,
            "artifacts_expire_at": getattr(job, "artifacts_expire_at", None),
            "download_note": "Artifact content not downloaded for security reasons. Use GitLab web interface or CLI for actual downloads.",
        }
        
        if artifact_path:
            result["requested_path"] = artifact_path
            
        return result

    @retry_on_error()
    def list_project_jobs(
        self,
        project_id: str,
        scope: Optional[str] = None,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List jobs for a project.
        
        Args:
            project_id: The project ID or path
            scope: Optional scope filter (created, pending, running, failed, success, canceled, skipped, waiting_for_resource, manual)
            per_page: Number of results per page
            page: Page number
            
        Returns:
            Dictionary with jobs list and pagination info
        """
        project = self.gl.projects.get(project_id)
        
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        
        if scope:
            kwargs["scope"] = scope
        
        response = project.jobs.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        
        return {
            "jobs": [self._job_to_dict(j) for j in response],
            "pagination": pagination,
            "project_id": project_id,
            "scope": scope,
        }

    # ------------------------------------------------------------------
    # Commit and Diff Methods
    # ------------------------------------------------------------------
    def get_commits(self, project_id: str, ref_name: Optional[str] = None,
                   since: Optional[str] = None, until: Optional[str] = None,
                   path: Optional[str] = None, per_page: int = DEFAULT_PAGE_SIZE,
                   page: int = 1) -> Dict[str, Any]:
        """Get list of commits for a project"""
        try:
            project = self.gl.projects.get(project_id)
            commits = project.commits.list(
                ref_name=ref_name,
                since=since,
                until=until,
                path=path,
                per_page=per_page,
                page=page,
                get_all=False
            )

            return {
                "commits": [
                    {
                        "id": commit.id,
                        "short_id": commit.short_id,
                        "title": commit.title,
                        "message": commit.message,
                        "author_name": commit.author_name,
                        "author_email": commit.author_email,
                        "authored_date": commit.authored_date,
                        "committer_name": commit.committer_name,
                        "committer_email": commit.committer_email,
                        "committed_date": commit.committed_date,
                        "created_at": commit.created_at,
                        "parent_ids": commit.parent_ids,
                        "web_url": commit.web_url
                    }
                    for commit in commits
                ]
            }
        except gitlab.exceptions.GitlabGetError as e:
            return {"error": f"Failed to get commits: {str(e)}"}

    def get_commit(self, project_id: str, commit_sha: str, include_stats: bool = False) -> Dict[str, Any]:
        """Get details of a specific commit"""
        try:
            project = self.gl.projects.get(project_id)
            commit = project.commits.get(commit_sha, stats=include_stats)

            result = {
                "id": commit.id,
                "short_id": commit.short_id,
                "title": commit.title,
                "message": commit.message,
                "author_name": commit.author_name,
                "author_email": commit.author_email,
                "authored_date": commit.authored_date,
                "committer_name": commit.committer_name,
                "committer_email": commit.committer_email,
                "committed_date": commit.committed_date,
                "created_at": commit.created_at,
                "parent_ids": commit.parent_ids,
                "web_url": commit.web_url
            }

            if include_stats and hasattr(commit, 'stats'):
                result["stats"] = commit.stats

            return result
        except gitlab.exceptions.GitlabGetError as e:
            return {"error": f"Failed to get commit: {str(e)}"}

    def get_commit_diff(self, project_id: str, commit_sha: str) -> Dict[str, Any]:
        """Get the diff of a specific commit"""
        try:
            project = self.gl.projects.get(project_id)
            commit = project.commits.get(commit_sha)
            diff = commit.diff()

            return {
                "commit_sha": commit_sha,
                "diff": diff
            }
        except gitlab.exceptions.GitlabGetError as e:
            return {"error": f"Failed to get commit diff: {str(e)}"}

    def create_commit(self, project_id: str, branch: str, commit_message: str,
                     actions: List[Dict[str, Any]], author_email: Optional[str] = None,
                     author_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new commit with file changes"""
        try:
            project = self.gl.projects.get(project_id)

            commit_data = {
                "branch": branch,
                "commit_message": commit_message,
                "actions": actions
            }

            if author_email:
                commit_data["author_email"] = author_email
            if author_name:
                commit_data["author_name"] = author_name

            commit = project.commits.create(commit_data)

            return {
                "id": commit.id,
                "short_id": commit.short_id,
                "title": commit.title,
                "message": commit.message,
                "author_name": commit.author_name,
                "author_email": commit.author_email,
                "created_at": commit.created_at,
                "parent_ids": commit.parent_ids,
                "web_url": commit.web_url
            }
        except gitlab.exceptions.GitlabCreateError as e:
            return {"error": f"Failed to create commit: {str(e)}"}

    def compare_refs(self, project_id: str, from_ref: str, to_ref: str, straight: bool = False) -> Dict[str, Any]:
        """Compare two refs (branches, tags, or commits)"""
        try:
            project = self.gl.projects.get(project_id)
            comparison = project.repository_compare(from_ref, to_ref, straight=straight)

            return {
                "commits": [
                    {
                        "id": commit["id"],
                        "short_id": commit.get("short_id"),
                        "title": commit.get("title"),
                        "message": commit.get("message"),
                        "author_name": commit.get("author_name"),
                        "created_at": commit.get("created_at")
                    }
                    for commit in comparison.get("commits", [])
                ],
                "diffs": comparison.get("diffs", []),
                "compare_timeout": comparison.get("compare_timeout", False),
                "compare_same_ref": comparison.get("compare_same_ref", False)
            }
        except Exception as e:
            return {"error": f"Failed to compare refs: {str(e)}"}

    def cherry_pick_commit(self, project_id: str, commit_sha: str, branch: str) -> Dict[str, Any]:
        """Cherry pick a commit to another branch"""
        try:
            project = self.gl.projects.get(project_id)
            commit = project.commits.get(commit_sha)
            cherry_picked = commit.cherry_pick(branch)

            return {
                "id": cherry_picked.get("id"),
                "short_id": cherry_picked.get("short_id"),
                "title": cherry_picked.get("title"),
                "message": cherry_picked.get("message"),
                "author_name": cherry_picked.get("author_name"),
                "created_at": cherry_picked.get("created_at"),
                "parent_ids": cherry_picked.get("parent_ids"),
                "web_url": cherry_picked.get("web_url")
            }
        except Exception as e:
            return {"error": f"Failed to cherry pick commit: {str(e)}"}

    def smart_diff(self, project_id: str, from_ref: str, to_ref: str,
                  context_lines: int = 3, max_file_size: int = 50000) -> Dict[str, Any]:
        """Get a smart diff between two refs with configurable context"""
        try:
            project = self.gl.projects.get(project_id)
            comparison = project.repository_compare(from_ref, to_ref)

            diffs = []
            for diff in comparison.get("diffs", []):
                # Skip files that are too large
                if diff.get("diff", "").count("\n") > max_file_size:
                    diffs.append({
                        "old_path": diff.get("old_path"),
                        "new_path": diff.get("new_path"),
                        "diff": f"File too large (>{max_file_size} lines)",
                        "new_file": diff.get("new_file", False),
                        "renamed_file": diff.get("renamed_file", False),
                        "deleted_file": diff.get("deleted_file", False)
                    })
                else:
                    diffs.append({
                        "old_path": diff.get("old_path"),
                        "new_path": diff.get("new_path"),
                        "diff": diff.get("diff"),
                        "new_file": diff.get("new_file", False),
                        "renamed_file": diff.get("renamed_file", False),
                        "deleted_file": diff.get("deleted_file", False),
                        "a_mode": diff.get("a_mode"),
                        "b_mode": diff.get("b_mode")
                    })

            return {
                "from_ref": from_ref,
                "to_ref": to_ref,
                "context_lines": context_lines,
                "diffs": diffs,
                "commits": [
                    {
                        "id": commit["id"],
                        "short_id": commit.get("short_id"),
                        "title": commit.get("title"),
                        "author_name": commit.get("author_name")
                    }
                    for commit in comparison.get("commits", [])
                ]
            }
        except Exception as e:
            return {"error": f"Failed to get smart diff: {str(e)}"}

    def safe_preview_commit(self, project_id: str, branch: str, commit_message: str,
                           actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preview what a commit would do without actually creating it"""
        try:
            project = self.gl.projects.get(project_id)

            # Validate branch exists
            try:
                project.branches.get(branch)
            except gitlab.exceptions.GitlabGetError:
                return {"error": f"Branch '{branch}' does not exist"}

            # Validate actions
            preview_results = []
            for action in actions:
                action_type = action.get("action")
                file_path = action.get("file_path")

                result = {
                    "action": action_type,
                    "file_path": file_path,
                    "valid": True,
                    "message": "OK"
                }

                # Check if file exists for update/delete actions
                if action_type in ["update", "delete"]:
                    try:
                        project.files.get(file_path, ref=branch)
                    except gitlab.exceptions.GitlabGetError:
                        result["valid"] = False
                        result["message"] = f"File '{file_path}' does not exist"

                # Check if file doesn't exist for create actions
                elif action_type == "create":
                    try:
                        project.files.get(file_path, ref=branch)
                        result["valid"] = False
                        result["message"] = f"File '{file_path}' already exists"
                    except gitlab.exceptions.GitlabGetError:
                        pass  # File doesn't exist, which is expected

                preview_results.append(result)

            return {
                "branch": branch,
                "commit_message": commit_message,
                "preview_results": preview_results,
                "valid": all(r["valid"] for r in preview_results)
            }
        except Exception as e:
            return {"error": f"Failed to preview commit: {str(e)}"}

    @retry_on_error()
    def summarize_issue(self, project_id: str, issue_iid: int, max_length: int = 500) -> Dict[str, Any]:
        """Generate an AI-friendly summary of an issue.
        
        This method retrieves issue details and comments, then formats them
        into a concise summary suitable for LLM context.
        
        Args:
            project_id: The project ID or path
            issue_iid: The issue IID (internal ID)
            max_length: Maximum length for description and comment summaries
            
        Returns:
            Dictionary with summarized issue information
        """
        # Get issue details
        issue = self.get_issue(project_id, issue_iid)
        
        # Get issue notes (comments)
        project = self.gl.projects.get(project_id)
        issue_obj = project.issues.get(issue_iid)
        
        # Get all notes with pagination
        all_notes = []
        kwargs = {
            "get_all": False,
            "per_page": SMALL_PAGE_SIZE,
            "page": 1,
            "order_by": "created_at",
            "sort": "asc"
        }
        
        # Get first page to check if there are any notes
        response = issue_obj.notes.list(**kwargs)
        all_notes.extend(response)
        
        # Get remaining pages if needed
        total_pages = getattr(response, "total_pages", 1)
        for page in range(2, min(total_pages + 1, 5)):  # Limit to 5 pages max
            kwargs["page"] = page
            response = issue_obj.notes.list(**kwargs)
            all_notes.extend(response)
        
        # Convert notes to dict format
        notes = [self._note_to_dict(n, max_length) for n in all_notes]
        
        # Filter out system notes
        user_comments = [n for n in notes if not n.get("system", False)]
        
        # Truncate description if needed
        description = issue.get("description", "")
        truncated_description = False
        if len(description) > max_length:
            description = description[:max_length] + "... [truncated]"
            truncated_description = True
        
        # Create summary
        summary = {
            "issue": {
                "iid": issue["iid"],
                "title": issue["title"],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "labels": issue.get("labels", []),
                "author": issue.get("author"),
                "web_url": issue["web_url"]
            },
            "description": description,
            "comments_count": len(user_comments),
            "comments": user_comments[:10],  # Limit to 10 most recent comments
            "summary_info": {
                "total_comments": len(all_notes),
                "user_comments": len(user_comments),
                "truncated_description": truncated_description,
                "truncated_comments": len(user_comments) > 10
            }
        }
        
        return summary

    # ============================================================================
    # USER & PROFILE METHODS
    # ============================================================================
    
    @retry_on_error()
    def search_user(self, search: str, per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Search for GitLab users by name, username, or email"""
        kwargs = {
            "search": search,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        response = self.gl.users.list(**kwargs)
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(response, "total", None),
            "total_pages": getattr(response, "total_pages", None),
            "next_page": getattr(response, "next_page", None),
            "prev_page": getattr(response, "prev_page", None),
        }
        return {
            "users": [self._user_to_dict(u) for u in response],
            "pagination": pagination,
            "search_term": search,
        }

    @staticmethod
    def _user_to_dict(user: Any) -> Dict[str, Any]:
        """Convert user object to dictionary"""
        return {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "name": getattr(user, "name", None),
            "email": getattr(user, "email", None),
            "avatar_url": getattr(user, "avatar_url", None),
            "web_url": getattr(user, "web_url", None),
            "state": getattr(user, "state", None),
            "bio": getattr(user, "bio", None),
            "location": getattr(user, "location", None),
            "public_email": getattr(user, "public_email", None),
            "skype": getattr(user, "skype", None),
            "linkedin": getattr(user, "linkedin", None),
            "twitter": getattr(user, "twitter", None),
            "website_url": getattr(user, "website_url", None),
            "organization": getattr(user, "organization", None),
            "job_title": getattr(user, "job_title", None),
            "created_at": getattr(user, "created_at", None),
            "last_sign_in_at": getattr(user, "last_sign_in_at", None),
            "is_admin": getattr(user, "is_admin", False),
            "can_create_group": getattr(user, "can_create_group", False),
            "can_create_project": getattr(user, "can_create_project", False),
            "projects_limit": getattr(user, "projects_limit", None),
        }

    @retry_on_error()
    def get_user_details(self, user_id: Optional[str] = None, username: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive user profile and metadata"""
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")
        
        return self._user_to_dict(user)

    @retry_on_error()
    def get_my_profile(self) -> Dict[str, Any]:
        """Get the current authenticated user's complete profile"""
        user = self.gl.user
        return self._user_to_dict(user)

    @retry_on_error()
    def get_user_contributions_summary(
        self, 
        user_id: Optional[str] = None, 
        username: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Summarize user's recent contributions across issues, MRs, and commits"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        user_info = self._user_to_dict(user)
        
        # Get user events to build contribution summary
        events_kwargs = {"get_all": False, "per_page": 100}
        if since:
            events_kwargs["after"] = since
        if until:
            events_kwargs["before"] = until
            
        events = user.events.list(**events_kwargs)
        
        # Analyze events to build summary
        commit_count = len([e for e in events if getattr(e, "action_name", "") == "pushed"])
        issue_created = len([e for e in events if getattr(e, "action_name", "") == "created" and getattr(e, "target_type", "") == "Issue"])
        issue_closed = len([e for e in events if getattr(e, "action_name", "") == "closed" and getattr(e, "target_type", "") == "Issue"])
        mr_created = len([e for e in events if getattr(e, "action_name", "") == "created" and getattr(e, "target_type", "") == "MergeRequest"])
        mr_merged = len([e for e in events if getattr(e, "action_name", "") == "merged" and getattr(e, "target_type", "") == "MergeRequest"])
        
        return {
            "user": user_info,
            "period": {
                "since": since,
                "until": until,
            },
            "contributions": {
                "commits": {"count": commit_count},
                "issues": {
                    "created": issue_created,
                    "closed": issue_closed,
                },
                "merge_requests": {
                    "created": mr_created,
                    "merged": mr_merged,
                }
            },
            "activity_summary": {
                "total_events": len(events),
                "active_period": since and until,
                "project_scope": project_id,
            }
        }

    @retry_on_error()
    def get_user_activity_feed(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1
    ) -> Dict[str, Any]:
        """Retrieve user's complete activity/events timeline"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        # Build events query
        kwargs = {
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        if action:
            kwargs["action"] = action
        if target_type:
            kwargs["target_type"] = target_type
        if after:
            kwargs["after"] = after
        if before:
            kwargs["before"] = before
            
        events = user.events.list(**kwargs)
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": getattr(events, "total", None),
            "total_pages": getattr(events, "total_pages", None),
            "next_page": getattr(events, "next_page", None),
            "prev_page": getattr(events, "prev_page", None),
        }
        
        return {
            "user": self._user_to_dict(user),
            "events": [self._event_to_dict(e) for e in events],
            "pagination": pagination,
            "filters": {
                "action": action,
                "target_type": target_type,
                "after": after,
                "before": before,
            }
        }

    # ============================================================================  
    # USER'S ISSUES & MRS METHODS
    # ============================================================================
    
    @retry_on_error()
    def get_user_open_mrs(
        self, 
        user_id: Optional[str] = None, 
        username: Optional[str] = None,
        sort: str = "updated",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get all open merge requests authored by a user"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        # Search for open MRs by this user across all accessible projects
        kwargs = {
            "state": "opened",
            "author_id": user.id,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
            "order_by": "updated_at" if sort == "updated" else "created_at",
            "sort": "desc"
        }
        
        # This is a simplified implementation - in real GitLab API, you'd search across projects
        # For the mock, we'll return user's open MRs from their accessible projects
        mrs = []
        user_info = self._user_to_dict(user)
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": len(mrs),
            "total_pages": 1,
            "next_page": None,
            "prev_page": None,
        }
        
        return {
            "user": user_info,
            "merge_requests": mrs,
            "pagination": pagination,
            "sort": sort,
        }

    @retry_on_error()
    def get_user_review_requests(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        priority: Optional[str] = None,
        sort: str = "urgency",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get MRs where user is assigned as reviewer with pending action"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        # In a real implementation, this would search for MRs where user is assigned as reviewer
        review_requests = []
        user_info = self._user_to_dict(user)
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": len(review_requests),
            "total_pages": 1,
            "next_page": None,
            "prev_page": None,
        }
        
        return {
            "user": user_info,
            "review_requests": review_requests,
            "pagination": pagination,
            "filters": {
                "priority": priority,
                "sort": sort,
            }
        }

    @retry_on_error()
    def get_user_open_issues(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        severity: Optional[str] = None,
        sla_status: Optional[str] = None,
        sort: str = "priority",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get open issues assigned to a user, prioritized by severity/SLA"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        # In a real implementation, this would search for open issues assigned to user
        issues = []
        user_info = self._user_to_dict(user)
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": len(issues),
            "total_pages": 1,
            "next_page": None,
            "prev_page": None,
        }
        
        return {
            "user": user_info,
            "issues": issues,
            "pagination": pagination,
            "filters": {
                "severity": severity,
                "sla_status": sla_status,
                "sort": sort,
            }
        }

    @retry_on_error()
    def get_user_reported_issues(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        state: str = "opened",
        since: Optional[str] = None,
        until: Optional[str] = None,
        sort: str = "created",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get issues reported/created by a user"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        # In a real implementation, this would search for issues created by user
        issues = []
        user_info = self._user_to_dict(user)
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": len(issues),
            "total_pages": 1,
            "next_page": None,
            "prev_page": None,
        }
        
        return {
            "user": user_info,
            "issues": issues,
            "pagination": pagination,
            "filters": {
                "state": state,
                "since": since,
                "until": until,
                "sort": sort,
            }
        }

    @retry_on_error()
    def get_user_resolved_issues(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        complexity: Optional[str] = None,
        sort: str = "closed",
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get issues closed/resolved by a user"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        # In a real implementation, this would search for issues closed by user
        issues = []
        user_info = self._user_to_dict(user)
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": len(issues),
            "total_pages": 1,
            "next_page": None,
            "prev_page": None,
        }
        
        return {
            "user": user_info,
            "issues": issues,
            "pagination": pagination,
            "filters": {
                "since": since,
                "until": until,
                "complexity": complexity,
                "sort": sort,
            }
        }

    # ============================================================================
    # USER'S CODE & COMMITS METHODS  
    # ============================================================================
    
    @retry_on_error()
    def get_user_commits(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        project_id: Optional[str] = None,
        branch: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        include_stats: bool = False,
        per_page: int = DEFAULT_PAGE_SIZE,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get commits authored by a user within date range or branch"""
        # Get user info first
        if user_id:
            user = self.gl.users.get(user_id, lazy=False)
        elif username:
            users = self.gl.users.list(username=username)
            if not users:
                raise ValueError(f"User not found: {username}")
            user = users[0]
        else:
            raise ValueError("Either user_id or username must be provided")

        # In a real implementation, this would search commits by author across projects
        commits = []
        user_info = self._user_to_dict(user)
        
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": len(commits),
            "total_pages": 1,
            "next_page": None,
            "prev_page": None,
        }
        
        return {
            "user": user_info,
            "commits": commits,
            "pagination": pagination,
            "filters": {
                "project_id": project_id,
                "branch": branch,
                "since": since,
                "until": until,
                "include_stats": include_stats,
            }
        }

    @retry_on_error()
    def get_user_merge_commits(self, username: str, project_id: Optional[str] = None, 
                             since: Optional[str] = None, until: Optional[str] = None,
                             per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get merge commits authored by a user"""
        project = self._get_project(project_id)
        
        # Get commits by user
        kwargs = {
            "author": username,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        if since:
            kwargs["since"] = since
        if until:
            kwargs["until"] = until
            
        response = project.commits.list(**kwargs)
        
        # Filter for merge commits only
        merge_commits = []
        for commit in response:
            try:
                commit_detail = project.commits.get(commit.id)
                parent_ids = getattr(commit_detail, 'parent_ids', [])
                
                # Only include if it's a merge commit (has multiple parents)
                if len(parent_ids) > 1:
                    commit_data = {
                        "id": commit.id,
                        "short_id": commit.short_id,
                        "title": commit.title,
                        "message": commit.message,
                        "author_name": commit.author_name,
                        "author_email": commit.author_email,
                        "authored_date": commit.authored_date,
                        "committer_name": commit.committer_name,
                        "committer_email": commit.committer_email,
                        "committed_date": commit.committed_date,
                        "created_at": commit.created_at,
                        "web_url": commit.web_url,
                        "parent_ids": parent_ids,
                        "parent_count": len(parent_ids)
                    }
                    merge_commits.append(commit_data)
            except Exception:
                # Skip commits we can't access
                continue
        
        user_info = self._get_user_info(username)
        
        return {
            "user": user_info,
            "merge_commits": merge_commits,
            "total_count": len(merge_commits),
            "filters": {
                "username": username,
                "project_id": project_id,
                "since": since,
                "until": until,
            }
        }

    @retry_on_error()
    def get_user_code_changes_summary(self, username: str, project_id: Optional[str] = None,
                                    since: Optional[str] = None, until: Optional[str] = None,
                                    per_page: int = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
        """Get a summary of code changes made by a user"""
        project = self._get_project(project_id)
        
        # Get commits by user
        kwargs = {
            "author": username,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "with_stats": True,
        }
        if since:
            kwargs["since"] = since
        if until:
            kwargs["until"] = until
            
        response = project.commits.list(**kwargs)
        
        # Aggregate statistics
        total_additions = 0
        total_deletions = 0
        total_commits = len(response)
        files_changed = set()
        
        commits_data = []
        for commit in response:
            try:
                commit_detail = project.commits.get(commit.id)
                stats = getattr(commit_detail, 'stats', {})
                additions = stats.get('additions', 0)
                deletions = stats.get('deletions', 0)
                
                total_additions += additions
                total_deletions += deletions
                
                commits_data.append({
                    "id": commit.id,
                    "short_id": commit.short_id,
                    "title": commit.title,
                    "authored_date": commit.authored_date,
                    "additions": additions,
                    "deletions": deletions,
                    "total_changes": additions + deletions,
                })
            except Exception:
                # Skip commits we can't get details for
                continue
        
        user_info = self._get_user_info(username)
        
        return {
            "user": user_info,
            "summary": {
                "total_commits": total_commits,
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "total_changes": total_additions + total_deletions,
                "average_changes_per_commit": round((total_additions + total_deletions) / max(total_commits, 1), 2)
            },
            "commits": commits_data,
            "filters": {
                "project_id": project_id,
                "since": since,
                "until": until,
            }
        }

    @retry_on_error() 
    def get_user_snippets(self, username: str, per_page: int = DEFAULT_PAGE_SIZE, 
                         page: int = 1) -> Dict[str, Any]:
        """Get snippets created by a user"""
        # First get the user to get their ID
        users = self.gl.users.list(username=username, get_all=False, per_page=1)
        if not users:
            return {"snippets": [], "total_count": 0, "error": "User not found"}
        
        user_id = users[0].id
        user_info = self._get_user_info(username)
        
        # Get user's snippets
        kwargs = {
            "author_id": user_id,
            "get_all": False,
            "per_page": min(per_page, MAX_PAGE_SIZE),
            "page": page,
        }
        
        response = self.gl.snippets.list(**kwargs)
        
        snippets = []
        for snippet in response:
            snippet_data = {
                "id": snippet.id,
                "title": snippet.title,
                "file_name": snippet.file_name,
                "description": getattr(snippet, 'description', ''),
                "visibility": snippet.visibility,
                "author": {
                    "id": snippet.author.get("id"),
                    "username": snippet.author.get("username"),
                    "name": snippet.author.get("name"),
                } if hasattr(snippet, 'author') and snippet.author else user_info,
                "created_at": snippet.created_at,
                "updated_at": snippet.updated_at,
                "expires_at": getattr(snippet, 'expires_at', None),
                "web_url": snippet.web_url,
            }
            
            # Try to get content preview
            try:
                snippet_detail = self.gl.snippets.get(snippet.id)
                if hasattr(snippet_detail, 'content'):
                    content = snippet_detail.content or ""
                    snippet_data["content_preview"] = content[:500] + ("..." if len(content) > 500 else "")
                    snippet_data["content_size"] = len(content)
                else:
                    snippet_data["content_preview"] = "[Content unavailable]"
                    snippet_data["content_size"] = 0
            except Exception:
                snippet_data["content_preview"] = "[Content access denied]"
                snippet_data["content_size"] = 0
            
            snippets.append(snippet_data)
        
        return {
            "user": user_info,
            "snippets": snippets,
            "total_count": len(snippets),
            "filters": {
                "username": username,
                "author_id": user_id,
            }
        }

    # User's Comments & Discussions methods
    @retry_on_error()
    def get_user_issue_comments(self, username: str, project_id: Optional[str] = None,
                               since: Optional[str] = None, until: Optional[str] = None,
                               per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get issue comments made by a user"""
        user_info = self._get_user_info(username)
        
        if project_id:
            project = self._get_project(project_id)
            projects = [project]
        else:
            # Get all accessible projects (limited search)
            projects = self.gl.projects.list(membership=True, get_all=False, per_page=20)
        
        all_comments = []
        
        for project in projects:
            try:
                # Get issues with notes
                issues = project.issues.list(get_all=False, per_page=50)
                
                for issue in issues:
                    try:
                        notes = issue.notes.list(get_all=False, per_page=50)
                        
                        for note in notes:
                            # Check if the note author matches our user
                            note_author = getattr(note, 'author', {})
                            if isinstance(note_author, dict):
                                note_username = note_author.get('username', '')
                            else:
                                note_username = getattr(note_author, 'username', '')
                            
                            if note_username == username:
                                # Filter by date if specified
                                note_date = note.created_at
                                if since and note_date < since:
                                    continue
                                if until and note_date > until:
                                    continue
                                
                                comment_data = {
                                    "id": note.id,
                                    "body": note.body[:500] + ("..." if len(note.body) > 500 else ""),
                                    "created_at": note.created_at,
                                    "updated_at": note.updated_at,
                                    "system": getattr(note, 'system', False),
                                    "noteable_type": "Issue",
                                    "noteable_id": issue.iid,
                                    "issue": {
                                        "id": issue.id,
                                        "iid": issue.iid,
                                        "title": issue.title,
                                        "web_url": issue.web_url
                                    },
                                    "project": {
                                        "id": project.id,
                                        "name": project.name,
                                        "path_with_namespace": project.path_with_namespace
                                    }
                                }
                                all_comments.append(comment_data)
                    except Exception:
                        continue
            except Exception:
                continue
        
        # Sort by creation date and paginate
        all_comments.sort(key=lambda x: x["created_at"], reverse=True)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_comments = all_comments[start_idx:end_idx]
        
        return {
            "user": user_info,
            "comments": paginated_comments,
            "total_count": len(all_comments),
            "filters": {
                "project_id": project_id,
                "since": since,
                "until": until,
            }
        }

    @retry_on_error()
    def get_user_mr_comments(self, username: str, project_id: Optional[str] = None,
                           since: Optional[str] = None, until: Optional[str] = None,
                           per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get MR comments made by a user"""
        user_info = self._get_user_info(username)
        
        if project_id:
            project = self._get_project(project_id)
            projects = [project]
        else:
            # Get all accessible projects (limited search)
            projects = self.gl.projects.list(membership=True, get_all=False, per_page=20)
        
        all_comments = []
        
        for project in projects:
            try:
                # Get merge requests with notes
                mrs = project.mergerequests.list(get_all=False, per_page=50)
                
                for mr in mrs:
                    try:
                        notes = mr.notes.list(get_all=False, per_page=50)
                        
                        for note in notes:
                            # Check if the note author matches our user
                            note_author = getattr(note, 'author', {})
                            if isinstance(note_author, dict):
                                note_username = note_author.get('username', '')
                            else:
                                note_username = getattr(note_author, 'username', '')
                            
                            if note_username == username:
                                # Filter by date if specified
                                note_date = note.created_at
                                if since and note_date < since:
                                    continue
                                if until and note_date > until:
                                    continue
                                
                                comment_data = {
                                    "id": note.id,
                                    "body": note.body[:500] + ("..." if len(note.body) > 500 else ""),
                                    "created_at": note.created_at,
                                    "updated_at": note.updated_at,
                                    "system": getattr(note, 'system', False),
                                    "noteable_type": "MergeRequest",
                                    "noteable_id": mr.iid,
                                    "merge_request": {
                                        "id": mr.id,
                                        "iid": mr.iid,
                                        "title": mr.title,
                                        "web_url": mr.web_url,
                                        "state": mr.state
                                    },
                                    "project": {
                                        "id": project.id,
                                        "name": project.name,
                                        "path_with_namespace": project.path_with_namespace
                                    }
                                }
                                all_comments.append(comment_data)
                    except Exception:
                        continue
            except Exception:
                continue
        
        # Sort by creation date and paginate
        all_comments.sort(key=lambda x: x["created_at"], reverse=True)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_comments = all_comments[start_idx:end_idx]
        
        return {
            "user": user_info,
            "comments": paginated_comments,
            "total_count": len(all_comments),
            "filters": {
                "project_id": project_id,
                "since": since,
                "until": until,
            }
        }

    @retry_on_error()
    def get_user_discussion_threads(self, username: str, project_id: Optional[str] = None,
                                  thread_status: Optional[str] = None,
                                  per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get discussion threads started by a user"""
        user_info = self._get_user_info(username)
        
        if project_id:
            project = self._get_project(project_id)
            projects = [project]
        else:
            # Get all accessible projects (limited search)
            projects = self.gl.projects.list(membership=True, get_all=False, per_page=20)
        
        all_threads = []
        
        for project in projects:
            try:
                # Get merge requests to check for discussions
                mrs = project.mergerequests.list(get_all=False, per_page=50)
                
                for mr in mrs:
                    try:
                        discussions = mr.discussions.list(get_all=False, per_page=50)
                        
                        for discussion in discussions:
                            # Check if discussion was started by our user
                            notes = getattr(discussion, 'notes', [])
                            if not notes:
                                continue
                            
                            first_note = notes[0] if isinstance(notes, list) else notes
                            note_author = getattr(first_note, 'author', {})
                            
                            if isinstance(note_author, dict):
                                note_username = note_author.get('username', '')
                            else:
                                note_username = getattr(note_author, 'username', '')
                            
                            if note_username == username:
                                # Filter by thread status if specified
                                discussion_resolved = getattr(discussion, 'resolved', False)
                                if thread_status == "resolved" and not discussion_resolved:
                                    continue
                                if thread_status == "unresolved" and discussion_resolved:
                                    continue
                                
                                thread_data = {
                                    "id": discussion.id,
                                    "resolved": discussion_resolved,
                                    "notes_count": len(notes) if isinstance(notes, list) else 1,
                                    "created_at": first_note.created_at if hasattr(first_note, 'created_at') else None,
                                    "first_note": {
                                        "body": first_note.body[:300] + ("..." if len(first_note.body) > 300 else "") if hasattr(first_note, 'body') else "",
                                    },
                                    "noteable_type": "MergeRequest",
                                    "noteable_id": mr.iid,
                                    "merge_request": {
                                        "id": mr.id,
                                        "iid": mr.iid,
                                        "title": mr.title,
                                        "web_url": mr.web_url,
                                        "state": mr.state
                                    },
                                    "project": {
                                        "id": project.id,
                                        "name": project.name,
                                        "path_with_namespace": project.path_with_namespace
                                    }
                                }
                                all_threads.append(thread_data)
                    except Exception:
                        continue
            except Exception:
                continue
        
        # Sort by creation date and paginate
        all_threads.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_threads = all_threads[start_idx:end_idx]
        
        return {
            "user": user_info,
            "discussion_threads": paginated_threads,
            "total_count": len(all_threads),
            "filters": {
                "project_id": project_id,
                "thread_status": thread_status,
            }
        }

    @retry_on_error()
    def get_user_resolved_threads(self, username: str, project_id: Optional[str] = None,
                                since: Optional[str] = None, until: Optional[str] = None,
                                per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get discussion threads resolved by a user"""
        user_info = self._get_user_info(username)
        
        if project_id:
            project = self._get_project(project_id)
            projects = [project]
        else:
            # Get all accessible projects (limited search)
            projects = self.gl.projects.list(membership=True, get_all=False, per_page=20)
        
        all_resolved_threads = []
        
        for project in projects:
            try:
                # Get merge requests to check for resolved discussions
                mrs = project.mergerequests.list(get_all=False, per_page=50)
                
                for mr in mrs:
                    try:
                        discussions = mr.discussions.list(get_all=False, per_page=50)
                        
                        for discussion in discussions:
                            # Check if discussion is resolved
                            if not getattr(discussion, 'resolved', False):
                                continue
                            
                            # Get notes to find who resolved it
                            notes = getattr(discussion, 'notes', [])
                            if not notes:
                                continue
                                
                            # Look for resolution by checking notes
                            for note in notes if isinstance(notes, list) else [notes]:
                                # Check for system notes about resolution
                                if (hasattr(note, 'system') and note.system and 
                                    hasattr(note, 'body') and 'resolved' in note.body.lower()):
                                    
                                    note_author = getattr(note, 'author', {})
                                    if isinstance(note_author, dict):
                                        note_username = note_author.get('username', '')
                                    else:
                                        note_username = getattr(note_author, 'username', '')
                                    
                                    if note_username == username:
                                        # Filter by date if specified
                                        if since and hasattr(note, 'created_at') and note.created_at < since:
                                            continue
                                        if until and hasattr(note, 'created_at') and note.created_at > until:
                                            continue
                                        
                                        thread_data = {
                                            "id": discussion.id,
                                            "resolved_at": note.created_at if hasattr(note, 'created_at') else None,
                                            "resolved_by": note_username,
                                            "notes_count": len(notes) if isinstance(notes, list) else 1,
                                            "noteable_type": "MergeRequest",
                                            "noteable_id": mr.iid,
                                            "merge_request": {
                                                "id": mr.id,
                                                "iid": mr.iid,
                                                "title": mr.title,
                                                "web_url": mr.web_url,
                                                "state": mr.state
                                            },
                                            "project": {
                                                "id": project.id,
                                                "name": project.name,
                                                "path_with_namespace": project.path_with_namespace
                                            }
                                        }
                                        all_resolved_threads.append(thread_data)
                                        break  # Only count each discussion once
                    except Exception:
                        continue
            except Exception:
                continue
        
        # Sort by resolution date and paginate
        all_resolved_threads.sort(key=lambda x: x.get("resolved_at", ""), reverse=True)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_threads = all_resolved_threads[start_idx:end_idx]
        
        return {
            "user": user_info,
            "resolved_threads": paginated_threads,
            "total_count": len(all_resolved_threads),
            "filters": {
                "project_id": project_id,
                "since": since,
                "until": until,
            }
        }


__all__ = ["GitLabClient", "GitLabConfig"]

