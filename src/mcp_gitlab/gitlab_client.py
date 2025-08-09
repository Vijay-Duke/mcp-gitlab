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
        description = issue.get("description", "") or ""
        if len(description) > max_length:
            description = description[:max_length] + "... [truncated]"
        
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
                "truncated_description": len(description) > max_length,
                "truncated_comments": len(user_comments) > 10
            }
        }
        
        return summary


__all__ = ["GitLabClient", "GitLabConfig"]

