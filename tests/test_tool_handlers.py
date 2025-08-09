"""Tests for tool handlers"""
import pytest
from unittest.mock import Mock
from mcp_gitlab.tool_handlers import (
    get_argument, require_argument, get_project_id_or_detect,
    require_project_id, handle_list_projects, handle_get_project,
    handle_get_current_project, handle_get_current_user, handle_get_user,
    handle_list_issues, handle_get_issue, handle_summarize_issue,
    handle_list_merge_requests, handle_get_merge_request,
    handle_update_merge_request, handle_close_merge_request,
    handle_merge_merge_request, handle_add_merge_request_comment,
    handle_get_merge_request_notes, handle_approve_merge_request,
    handle_get_merge_request_approvals, handle_get_merge_request_discussions,
    handle_resolve_discussion, handle_get_merge_request_changes,
    handle_rebase_merge_request, handle_search_projects,
    TOOL_HANDLERS
)
from mcp_gitlab.constants import (
    ERROR_NO_PROJECT, DEFAULT_PAGE_SIZE,
    TOOL_GET_CURRENT_USER, TOOL_GET_USER
)


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_get_argument_with_value(self):
        """Test get_argument returns value when present"""
        args = {"key": "value", "number": 42}
        assert get_argument(args, "key") == "value"
        assert get_argument(args, "number") == 42
    
    def test_get_argument_with_default(self):
        """Test get_argument returns default when key missing"""
        args = {"key": "value"}
        assert get_argument(args, "missing", "default") == "default"
        assert get_argument(args, "missing", 123) == 123
    
    def test_get_argument_with_none_args(self):
        """Test get_argument handles None arguments"""
        assert get_argument(None, "key", "default") == "default"
    
    def test_require_argument_success(self):
        """Test require_argument returns value when present"""
        args = {"key": "value"}
        assert require_argument(args, "key") == "value"
    
    def test_require_argument_missing(self):
        """Test require_argument raises error when missing"""
        args = {"other": "value"}
        with pytest.raises(ValueError, match="key is required"):
            require_argument(args, "key")
    
    def test_require_argument_none_args(self):
        """Test require_argument raises error with None args"""
        with pytest.raises(ValueError, match="key is required"):
            require_argument(None, "key")
    
    def test_get_project_id_or_detect_from_args(self):
        """Test getting project_id from arguments"""
        client = Mock()
        args = {"project_id": "123"}
        assert get_project_id_or_detect(client, args) == "123"
        client.get_project_from_git.assert_not_called()
    
    def test_get_project_id_or_detect_from_git(self):
        """Test detecting project_id from git"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "456"}
        args = {}
        assert get_project_id_or_detect(client, args) == "456"
        client.get_project_from_git.assert_called_once_with(".")
    
    def test_get_project_id_or_detect_not_found(self):
        """Test when project_id not found"""
        client = Mock()
        client.get_project_from_git.return_value = None
        assert get_project_id_or_detect(client, {}) is None
    
    def test_require_project_id_success(self):
        """Test require_project_id returns ID when found"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        assert require_project_id(client, {}) == "123"
    
    def test_require_project_id_failure(self):
        """Test require_project_id raises error when not found"""
        client = Mock()
        client.get_project_from_git.return_value = None
        with pytest.raises(ValueError, match=ERROR_NO_PROJECT):
            require_project_id(client, {})


class TestAuthenticationHandlers:
    """Test authentication and user handlers"""
    
    def test_handle_get_current_user(self):
        """Test getting current authenticated user"""
        client = Mock()
        client.get_current_user.return_value = {
            "id": 123,
            "username": "johndoe",
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        result = handle_get_current_user(client, None)
        
        client.get_current_user.assert_called_once()
        assert result["id"] == 123
        assert result["username"] == "johndoe"
    
    def test_handle_get_user_by_id(self):
        """Test getting user by ID"""
        client = Mock()
        client.get_user.return_value = {
            "id": 456,
            "username": "janedoe",
            "name": "Jane Doe"
        }
        
        result = handle_get_user(client, {"user_id": 456})
        
        client.get_user.assert_called_once_with(user_id=456, username=None)
        assert result["id"] == 456
        assert result["username"] == "janedoe"
    
    def test_handle_get_user_by_username(self):
        """Test getting user by username"""
        client = Mock()
        client.get_user.return_value = {
            "id": 789,
            "username": "testuser",
            "name": "Test User"
        }
        
        result = handle_get_user(client, {"username": "testuser"})
        
        client.get_user.assert_called_once_with(user_id=None, username="testuser")
        assert result["username"] == "testuser"
    
    def test_handle_get_user_not_found(self):
        """Test getting user that doesn't exist"""
        client = Mock()
        client.get_user.return_value = None
        
        with pytest.raises(ValueError, match="User not found: 999"):
            handle_get_user(client, {"user_id": 999})
    
    def test_handle_get_user_no_params(self):
        """Test getting user without parameters"""
        client = Mock()
        
        with pytest.raises(ValueError, match="Either user_id or username must be provided"):
            handle_get_user(client, {})


class TestProjectHandlers:
    """Test project management handlers"""
    
    def test_handle_list_projects(self):
        """Test listing projects"""
        client = Mock()
        client.get_projects.return_value = {"data": [{"id": 1}]}
        
        result = handle_list_projects(client, {
            "owned": True,
            "search": "test",
            "per_page": 10,
            "page": 2
        })
        
        client.get_projects.assert_called_once_with(
            owned=True, search="test", per_page=10, page=2
        )
        assert result == {"data": [{"id": 1}]}
    
    def test_handle_list_projects_defaults(self):
        """Test listing projects with defaults"""
        client = Mock()
        client.get_projects.return_value = {"data": []}
        
        handle_list_projects(client, None)
        
        client.get_projects.assert_called_once_with(
            owned=False, search=None, per_page=DEFAULT_PAGE_SIZE, page=1
        )
    
    def test_handle_get_project(self):
        """Test getting single project"""
        client = Mock()
        client.get_project.return_value = {"id": 123}
        
        result = handle_get_project(client, {"project_id": "group/project"})
        
        client.get_project.assert_called_once_with("group/project")
        assert result == {"id": 123}
    
    def test_handle_get_project_missing_id(self):
        """Test getting project without ID"""
        client = Mock()
        
        with pytest.raises(ValueError, match="project_id is required"):
            handle_get_project(client, {})
    
    def test_handle_search_projects(self):
        """Test searching projects"""
        client = Mock()
        client.search_projects.return_value = {"data": []}

        result = handle_search_projects(client, {"search": "test", "per_page": 10, "page": 2})

        client.search_projects.assert_called_once_with("test", 10, 2)
        assert result == {"data": []}

    def test_handle_search_projects_defaults(self):
        """Test searching projects with default pagination"""
        client = Mock()
        client.search_projects.return_value = {"data": []}

        result = handle_search_projects(client, {"search": "test"})

        client.search_projects.assert_called_once_with("test", DEFAULT_PAGE_SIZE, 1)
        assert result == {"data": []}

    def test_handle_search_projects_missing_term(self):
        """Test searching projects requires term"""
        client = Mock()

        with pytest.raises(ValueError, match="search is required"):
            handle_search_projects(client, {})

    def test_handle_get_current_project_found(self):
        """Test getting current project via git detection"""
        client = Mock()
        client.get_current_project.return_value = {"id": 123}

        result = handle_get_current_project(client, {"path": "/repo"})

        client.get_current_project.assert_called_once_with("/repo")
        assert result == {"id": 123}

    def test_handle_get_current_project_not_found(self):
        """Test getting current project when not found"""
        client = Mock()
        client.get_current_project.return_value = None

        result = handle_get_current_project(client, {})

        client.get_current_project.assert_called_once_with(".")
        assert result == {"error": ERROR_NO_PROJECT}


class TestIssueHandlers:
    """Test issue handlers"""
    
    def test_handle_list_issues(self):
        """Test listing issues"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_issues.return_value = {"data": [{"iid": 1}]}
        
        result = handle_list_issues(client, {
            "state": "closed",
            "per_page": 20,
            "page": 3
        })
        
        client.get_issues.assert_called_once_with("123", "closed", 20, 3)
        assert result == {"data": [{"iid": 1}]}
    
    def test_handle_get_issue(self):
        """Test getting single issue"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_issue.return_value = {"iid": 42}
        
        result = handle_get_issue(client, {"issue_iid": 42})
        
        client.get_issue.assert_called_once_with("123", 42)
        assert result == {"iid": 42}
    
    def test_handle_summarize_issue(self):
        """Test summarizing an issue"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.summarize_issue.return_value = {
            "issue": {"iid": 42, "title": "Test Issue"},
            "description": "Truncated description...",
            "comments_count": 5,
            "comments": [],
            "summary_info": {
                "total_comments": 10,
                "user_comments": 5,
                "truncated_description": True,
                "truncated_comments": False
            }
        }
        
        result = handle_summarize_issue(client, {
            "issue_iid": 42,
            "max_length": 300
        })
        
        client.summarize_issue.assert_called_once_with("123", 42, 300)
        assert result["issue"]["iid"] == 42
        assert result["comments_count"] == 5
        assert result["summary_info"]["user_comments"] == 5


class TestMergeRequestHandlers:
    """Test merge request handlers"""
    
    def test_handle_list_merge_requests(self):
        """Test listing merge requests"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_merge_requests.return_value = {"data": [{"iid": 10}]}
        
        result = handle_list_merge_requests(client, {"state": "merged"})
        
        client.get_merge_requests.assert_called_once_with(
            "123", "merged", DEFAULT_PAGE_SIZE, 1
        )
        assert result == {"data": [{"iid": 10}]}
    
    def test_handle_get_merge_request_notes(self):
        """Test getting MR notes"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_merge_request_notes.return_value = {"data": [{"id": 1}]}
        
        result = handle_get_merge_request_notes(client, {
            "mr_iid": 42,
            "per_page": 10,
            "sort": "desc",
            "max_body_length": 100
        })
        
        client.get_merge_request_notes.assert_called_once_with(
            "123", 42, 10, 1, "desc", "created_at", 100
        )
        assert result == {"data": [{"id": 1}]}

    def test_handle_get_merge_request(self):
        """Test retrieving a single merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_merge_request.return_value = {"iid": 5}

        result = handle_get_merge_request(client, {"mr_iid": 5})

        client.get_merge_request.assert_called_once_with("123", 5)
        assert result == {"iid": 5}

    def test_handle_update_merge_request(self):
        """Test updating merge request with optional fields"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.update_merge_request.return_value = {"iid": 5, "title": "New"}

        args = {"mr_iid": 5, "title": "New", "labels": "bug"}
        result = handle_update_merge_request(client, args)

        client.update_merge_request.assert_called_once_with("123", 5, title="New", labels="bug")
        assert result == {"iid": 5, "title": "New"}

    def test_handle_close_merge_request(self):
        """Test closing a merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.close_merge_request.return_value = {"iid": 5, "state": "closed"}

        result = handle_close_merge_request(client, {"mr_iid": 5})

        client.close_merge_request.assert_called_once_with("123", 5)
        assert result == {"iid": 5, "state": "closed"}

    def test_handle_merge_merge_request(self):
        """Test merging a merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.merge_merge_request.return_value = {"iid": 5, "state": "merged"}

        args = {
            "mr_iid": 5,
            "merge_when_pipeline_succeeds": True,
            "squash": True,
            "merge_commit_message": "msg"
        }
        result = handle_merge_merge_request(client, args)

        client.merge_merge_request.assert_called_once_with(
            "123", 5, True, None, "msg", None, True
        )
        assert result == {"iid": 5, "state": "merged"}

    def test_handle_add_merge_request_comment(self):
        """Test adding comment to merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.add_merge_request_comment.return_value = {"id": 1}

        result = handle_add_merge_request_comment(client, {"mr_iid": 5, "body": "hi"})

        client.add_merge_request_comment.assert_called_once_with("123", 5, "hi")
        assert result == {"id": 1}

    def test_handle_approve_merge_request(self):
        """Test approving a merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.approve_merge_request.return_value = {"approved": True}

        result = handle_approve_merge_request(client, {"mr_iid": 5})

        client.approve_merge_request.assert_called_once_with("123", 5)
        assert result == {"approved": True}

    def test_handle_get_merge_request_approvals(self):
        """Test retrieving approvals for merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_merge_request_approvals.return_value = {"approved": False}

        result = handle_get_merge_request_approvals(client, {"mr_iid": 5})

        client.get_merge_request_approvals.assert_called_once_with("123", 5)
        assert result == {"approved": False}

    def test_handle_get_merge_request_discussions(self):
        """Test getting discussions for a merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_merge_request_discussions.return_value = {"discussions": []}

        result = handle_get_merge_request_discussions(client, {"mr_iid": 5, "per_page": 5, "page": 2})

        client.get_merge_request_discussions.assert_called_once_with("123", 5, 5, 2)
        assert result == {"discussions": []}

    def test_handle_resolve_discussion(self):
        """Test resolving a discussion thread"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.resolve_discussion.return_value = {"discussion_id": "abc"}

        result = handle_resolve_discussion(client, {"mr_iid": 5, "discussion_id": "abc"})

        client.resolve_discussion.assert_called_once_with("123", 5, "abc")
        assert result == {"discussion_id": "abc"}

    def test_handle_get_merge_request_changes(self):
        """Test retrieving merge request changes"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.get_merge_request_changes.return_value = {"changes": []}

        result = handle_get_merge_request_changes(client, {"mr_iid": 5})

        client.get_merge_request_changes.assert_called_once_with("123", 5)
        assert result == {"changes": []}

    def test_handle_rebase_merge_request(self):
        """Test rebasing a merge request"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": "123"}
        client.rebase_merge_request.return_value = {"rebase_in_progress": False}

        result = handle_rebase_merge_request(client, {"mr_iid": 5})

        client.rebase_merge_request.assert_called_once_with("123", 5)
        assert result == {"rebase_in_progress": False}


class TestToolHandlerMapping:
    """Test tool handler mapping"""
    
    def test_all_handlers_mapped(self):
        """Test all handlers are in the mapping"""
        expected_tools = [
            "gitlab_list_projects",
            "gitlab_get_project",
            "gitlab_get_current_project",
            "gitlab_get_current_user",
            "gitlab_get_user",
            "gitlab_list_issues",
            "gitlab_get_issue",
            "gitlab_list_merge_requests",
            "gitlab_get_merge_request",
            "gitlab_get_merge_request_notes",
            "gitlab_get_file_content",
            "gitlab_list_repository_tree",
            "gitlab_list_commits",
            "gitlab_get_commit",
            "gitlab_get_commit_diff",
            "gitlab_search_projects",
            "gitlab_search_in_project",
            "gitlab_list_branches",
            "gitlab_list_pipelines",
            "gitlab_list_user_events",
            # Newly implemented merge request operations
            "gitlab_update_merge_request",
            "gitlab_close_merge_request",
            "gitlab_merge_merge_request",
            "gitlab_add_merge_request_comment",
            "gitlab_approve_merge_request",
            "gitlab_get_merge_request_approvals",
            "gitlab_get_merge_request_discussions",
            "gitlab_resolve_discussion",
            "gitlab_get_merge_request_changes",
            "gitlab_rebase_merge_request",
        ]
        
        for tool in expected_tools:
            assert tool in TOOL_HANDLERS
            assert callable(TOOL_HANDLERS[tool])