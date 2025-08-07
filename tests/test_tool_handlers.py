"""Tests for tool handlers"""
import pytest
from unittest.mock import Mock
from mcp_gitlab.tool_handlers import (
    get_argument, require_argument, get_project_id_or_detect,
    require_project_id, handle_list_projects, handle_get_project,
    handle_detect_project, handle_list_issues, handle_get_issue,
    handle_list_merge_requests, handle_get_merge_request,
    handle_get_merge_request_notes, TOOL_HANDLERS
)
from mcp_gitlab.constants import ERROR_NO_PROJECT, DEFAULT_PAGE_SIZE


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
    
    def test_handle_detect_project_found(self):
        """Test detecting project successfully"""
        client = Mock()
        client.get_project_from_git.return_value = {"id": 123}
        
        result = handle_detect_project(client, {"path": "/some/path"})
        
        client.get_project_from_git.assert_called_once_with("/some/path")
        assert result == {"id": 123}
    
    def test_handle_detect_project_not_found(self):
        """Test detecting project when not found"""
        client = Mock()
        client.get_project_from_git.return_value = None
        
        result = handle_detect_project(client, {})
        
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


class TestToolHandlerMapping:
    """Test tool handler mapping"""
    
    def test_all_handlers_mapped(self):
        """Test all handlers are in the mapping"""
        expected_tools = [
            "gitlab_list_projects",
            "gitlab_get_project", 
            "gitlab_detect_project",
            "gitlab_list_issues",
            "gitlab_get_issue",
            "gitlab_list_merge_requests",
            "gitlab_get_merge_request",
            "gitlab_get_merge_request_notes",
            "gitlab_get_file_content",
            "gitlab_get_repository_tree",
            "gitlab_get_commits",
            "gitlab_get_commit",
            "gitlab_get_commit_diff",
            "gitlab_search_projects",
            "gitlab_search_in_project",
            "gitlab_list_branches",
            "gitlab_list_pipelines",
            "gitlab_get_user_events"
        ]
        
        for tool in expected_tools:
            assert tool in TOOL_HANDLERS
            assert callable(TOOL_HANDLERS[tool])