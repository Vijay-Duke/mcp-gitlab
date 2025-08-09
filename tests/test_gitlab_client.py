"""Tests for GitLabClient class"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import gitlab
from mcp_gitlab.gitlab_client import GitLabClient, GitLabConfig
from mcp_gitlab.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


def mock_paginated_response(items, total=None, total_pages=1, next_page=None, prev_page=None):
    """Create a mock paginated response"""
    # Create a list-like object with pagination attributes
    class MockPaginatedList(list):
        def __init__(self, items):
            super().__init__(items)
            
    response = MockPaginatedList(items)
    response.total = total or len(items)
    response.total_pages = total_pages
    response.next_page = next_page
    response.prev_page = prev_page
    return response


class TestGitLabClient:
    """Test cases for GitLabClient class"""
    
    @pytest.fixture
    def mock_gitlab(self):
        """Mock gitlab.Gitlab instance"""
        with patch('gitlab.Gitlab') as mock:
            yield mock
    
    @pytest.fixture
    def client(self, mock_gitlab):
        """Create GitLabClient instance with mocked gitlab"""
        config = GitLabConfig(
            url="https://gitlab.com",
            private_token="test-token"
        )
        mock_instance = Mock()
        mock_gitlab.return_value = mock_instance
        mock_instance.auth.return_value = None
        
        return GitLabClient(config)
    
    @pytest.mark.unit
    def test_init_with_private_token(self, mock_gitlab):
        """Test initialization with private token"""
        config = GitLabConfig(
            url="https://gitlab.com",
            private_token="test-token"
        )
        _ = GitLabClient(config)
        
        mock_gitlab.assert_called_once_with(
            "https://gitlab.com",
            private_token="test-token"
        )
    
    @pytest.mark.unit
    def test_init_with_oauth_token(self, mock_gitlab):
        """Test initialization with OAuth token"""
        config = GitLabConfig(
            url="https://gitlab.com",
            oauth_token="oauth-token"
        )
        _ = GitLabClient(config)
        
        mock_gitlab.assert_called_once_with(
            "https://gitlab.com",
            oauth_token="oauth-token"
        )
    
    @pytest.mark.unit
    def test_init_no_token_raises_error(self):
        """Test initialization without token raises ValueError"""
        config = GitLabConfig(url="https://gitlab.com")
        
        with pytest.raises(ValueError, match="Either private_token or oauth_token must be provided"):
            GitLabClient(config)
    
    @pytest.mark.unit
    def test_get_projects(self, client):
        """Test getting projects list"""
        # Mock project objects with required attributes
        mock_project1 = Mock()
        mock_project1.id = 1
        mock_project1.name = "Project 1"
        mock_project1.path = "project-1"
        mock_project1.path_with_namespace = "group/project-1"
        mock_project1.description = "Description 1"
        mock_project1.web_url = "https://gitlab.com/group/project-1"
        mock_project1.visibility = "private"
        mock_project1.last_activity_at = "2024-01-01T00:00:00Z"
        
        mock_project2 = Mock()
        mock_project2.id = 2
        mock_project2.name = "Project 2"
        mock_project2.path = "project-2"
        mock_project2.path_with_namespace = "group/project-2"
        mock_project2.description = "Description 2"
        mock_project2.web_url = "https://gitlab.com/group/project-2"
        mock_project2.visibility = "public"
        mock_project2.last_activity_at = "2024-01-02T00:00:00Z"
        
        # Mock the response object with pagination attributes
        mock_response = mock_paginated_response([mock_project1, mock_project2], total=2)
        
        client.gl.projects.list.return_value = mock_response
        
        result = client.get_projects(owned=True, search="test", per_page=20, page=1)
        
        client.gl.projects.list.assert_called_once_with(
            owned=True,
            membership=True,
            search="test",
            per_page=20,
            page=1,
            get_all=False
        )
        
        assert "projects" in result
        assert len(result["projects"]) == 2
        assert result["projects"][0]["id"] == 1
        assert result["projects"][0]["name"] == "Project 1"
        assert result["projects"][1]["id"] == 2
        assert result["projects"][1]["name"] == "Project 2"
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["per_page"] == 20
        assert result["pagination"]["total"] == 2
    
    @pytest.mark.unit
    def test_get_project(self, client):
        """Test getting single project"""
        mock_project = Mock()
        mock_project.id = 1
        mock_project.name = "Test Project"
        mock_project.path = "project"
        mock_project.path_with_namespace = "group/project"
        mock_project.description = "Test description"
        mock_project.web_url = "https://gitlab.com/group/project"
        mock_project.visibility = "private"
        mock_project.last_activity_at = "2024-01-01T00:00:00Z"
        
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_project("group/project")
        
        client.gl.projects.get.assert_called_once_with("group/project")
        assert result["id"] == 1
        assert result["name"] == "Test Project"
        assert result["path_with_namespace"] == "group/project"
    
    @pytest.mark.unit
    def test_get_issues(self, client):
        """Test getting issues list"""
        mock_project = Mock()
        mock_issue1 = Mock()
        mock_issue1.id = 101
        mock_issue1.iid = 1
        mock_issue1.title = "Issue 1"
        mock_issue1.description = "Description 1"
        mock_issue1.state = "opened"
        mock_issue1.created_at = "2024-01-01T00:00:00Z"
        mock_issue1.updated_at = "2024-01-01T00:00:00Z"
        mock_issue1.labels = ["bug"]
        mock_issue1.web_url = "https://gitlab.com/group/project/issues/1"
        mock_issue1.author = {"username": "user1", "name": "User 1"}
        
        mock_issue2 = Mock()
        mock_issue2.id = 102
        mock_issue2.iid = 2
        mock_issue2.title = "Issue 2"
        mock_issue2.description = "Description 2"
        mock_issue2.state = "opened"
        mock_issue2.created_at = "2024-01-02T00:00:00Z"
        mock_issue2.updated_at = "2024-01-02T00:00:00Z"
        mock_issue2.labels = ["feature"]
        mock_issue2.web_url = "https://gitlab.com/group/project/issues/2"
        mock_issue2.author = {"username": "user2", "name": "User 2"}
        
        mock_response = mock_paginated_response([mock_issue1, mock_issue2], total=2)
        mock_project.issues.list.return_value = mock_response
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_issues("project-id", state="opened", per_page=10, page=2)
        
        client.gl.projects.get.assert_called_once_with("project-id")
        mock_project.issues.list.assert_called_once_with(
            state="opened",
            per_page=10,
            page=2,
            get_all=False
        )
        
        assert "issues" in result
        assert len(result["issues"]) == 2
        assert result["issues"][0]["iid"] == 1
        assert result["issues"][0]["title"] == "Issue 1"
        assert result["pagination"]["page"] == 2
        assert result["pagination"]["per_page"] == 10
    
    @pytest.mark.unit
    def test_get_issue(self, client):
        """Test getting single issue"""
        mock_project = Mock()
        mock_issue = Mock()
        mock_issue.id = 101
        mock_issue.iid = 1
        mock_issue.title = "Test Issue"
        mock_issue.description = "Test description"
        mock_issue.state = "opened"
        mock_issue.created_at = "2024-01-01T00:00:00Z"
        mock_issue.updated_at = "2024-01-01T00:00:00Z"
        mock_issue.labels = ["bug"]
        mock_issue.web_url = "https://gitlab.com/group/project/issues/1"
        mock_issue.author = {"username": "user1", "name": "User 1"}
        
        mock_project.issues.get.return_value = mock_issue
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_issue("project-id", 1)
        
        client.gl.projects.get.assert_called_once_with("project-id")
        mock_project.issues.get.assert_called_once_with(1, lazy=False)
        assert result["iid"] == 1
        assert result["title"] == "Test Issue"
        assert result["state"] == "opened"
    
    @pytest.mark.unit
    def test_summarize_issue(self, client):
        """Test summarizing an issue"""
        # Mock issue
        mock_issue = Mock()
        mock_issue.id = 101
        mock_issue.iid = 1
        mock_issue.title = "Test Issue"
        mock_issue.description = "This is a long description " * 50  # Long description
        mock_issue.state = "opened"
        mock_issue.created_at = "2024-01-01T00:00:00Z"
        mock_issue.updated_at = "2024-01-01T00:00:00Z"
        mock_issue.labels = ["bug", "high-priority"]
        mock_issue.web_url = "https://gitlab.com/group/project/issues/1"
        mock_issue.author = {"username": "user1", "name": "User 1"}
        
        # Mock notes
        mock_note1 = Mock()
        mock_note1.id = 201
        mock_note1.body = "This is the first comment"
        mock_note1.created_at = "2024-01-02T00:00:00Z"
        mock_note1.updated_at = "2024-01-02T00:00:00Z"
        mock_note1.author = {"username": "user2", "name": "User 2"}
        mock_note1.system = False
        mock_note1.noteable_type = "Issue"
        mock_note1.noteable_iid = 1
        mock_note1.resolvable = False
        mock_note1.resolved = False
        
        mock_note2 = Mock()
        mock_note2.id = 202
        mock_note2.body = "System note"
        mock_note2.created_at = "2024-01-03T00:00:00Z"
        mock_note2.updated_at = "2024-01-03T00:00:00Z"
        mock_note2.author = {"username": "system", "name": "System"}
        mock_note2.system = True
        mock_note2.noteable_type = "Issue"
        mock_note2.noteable_iid = 1
        mock_note2.resolvable = False
        mock_note2.resolved = False
        
        mock_note3 = Mock()
        mock_note3.id = 203
        mock_note3.body = "This is another user comment"
        mock_note3.created_at = "2024-01-04T00:00:00Z"
        mock_note3.updated_at = "2024-01-04T00:00:00Z"
        mock_note3.author = {"username": "user3", "name": "User 3"}
        mock_note3.system = False
        mock_note3.noteable_type = "Issue"
        mock_note3.noteable_iid = 1
        mock_note3.resolvable = False
        mock_note3.resolved = False
        
        # Mock responses
        mock_project = Mock()
        mock_project.issues.get.return_value = mock_issue
        
        mock_notes_response = mock_paginated_response(
            [mock_note1, mock_note2, mock_note3], 
            total=3, 
            total_pages=1
        )
        mock_issue.notes.list.return_value = mock_notes_response
        
        client.gl.projects.get.return_value = mock_project
        
        # Call the method
        result = client.summarize_issue("project-id", 1, max_length=100)
        
        # Assertions
        assert "issue" in result
        assert result["issue"]["iid"] == 1
        assert result["issue"]["title"] == "Test Issue"
        assert result["issue"]["state"] == "opened"
        assert result["issue"]["labels"] == ["bug", "high-priority"]
        
        assert "description" in result
        assert len(result["description"]) <= 100 + len("... [truncated]")
        assert result["description"].endswith("... [truncated]")
        
        assert "comments_count" in result
        assert result["comments_count"] == 2  # Only user comments, not system
        
        assert "comments" in result
        assert len(result["comments"]) == 2
        assert result["comments"][0]["body"] == "This is the first comment"
        assert result["comments"][1]["body"] == "This is another user comment"
        
        assert "summary_info" in result
        assert result["summary_info"]["total_comments"] == 3
        assert result["summary_info"]["user_comments"] == 2
        assert result["summary_info"]["truncated_description"] is True
        assert result["summary_info"]["truncated_comments"] is False
    
    @pytest.mark.unit
    def test_get_merge_requests(self, client):
        """Test getting merge requests list"""
        mock_project = Mock()
        mock_mr1 = Mock()
        mock_mr1.id = 201
        mock_mr1.iid = 1
        mock_mr1.title = "MR 1"
        mock_mr1.description = "Description 1"
        mock_mr1.state = "merged"
        mock_mr1.source_branch = "feature-1"
        mock_mr1.target_branch = "main"
        mock_mr1.created_at = "2024-01-01T00:00:00Z"
        mock_mr1.updated_at = "2024-01-01T00:00:00Z"
        mock_mr1.web_url = "https://gitlab.com/group/project/merge_requests/1"
        mock_mr1.author = {"username": "user1", "name": "User 1"}
        
        mock_mr2 = Mock()
        mock_mr2.id = 202
        mock_mr2.iid = 2
        mock_mr2.title = "MR 2"
        mock_mr2.description = "Description 2"
        mock_mr2.state = "merged"
        mock_mr2.source_branch = "feature-2"
        mock_mr2.target_branch = "main"
        mock_mr2.created_at = "2024-01-02T00:00:00Z"
        mock_mr2.updated_at = "2024-01-02T00:00:00Z"
        mock_mr2.web_url = "https://gitlab.com/group/project/merge_requests/2"
        mock_mr2.author = {"username": "user2", "name": "User 2"}
        
        mock_response = mock_paginated_response([mock_mr1, mock_mr2], total=2)
        mock_project.mergerequests.list.return_value = mock_response
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_merge_requests("project-id", state="merged")
        
        mock_project.mergerequests.list.assert_called_once_with(
            state="merged",
            per_page=DEFAULT_PAGE_SIZE,
            page=1,
            get_all=False
        )
        
        assert "merge_requests" in result
        assert len(result["merge_requests"]) == 2
        assert result["merge_requests"][0]["title"] == "MR 1"
        assert result["merge_requests"][0]["iid"] == 1
        assert result["pagination"]["total"] == 2
    
    @pytest.mark.unit
    def test_get_merge_request_notes(self, client):
        """Test getting merge request notes with truncation"""
        mock_project = Mock()
        mock_mr = Mock()
        mock_mr.title = "Test MR"
        mock_mr.web_url = "https://gitlab.com/group/project/merge_requests/1"
        
        # Create mock notes
        mock_note1 = Mock()
        mock_note1.id = 1
        mock_note1.body = "A" * 600  # Long body
        mock_note1.created_at = "2024-01-01T00:00:00Z"
        mock_note1.updated_at = "2024-01-01T00:00:00Z"
        mock_note1.author = {"username": "user1", "name": "User 1"}
        mock_note1.system = False
        mock_note1.noteable_type = "MergeRequest"
        mock_note1.noteable_iid = 1
        mock_note1.resolvable = False
        mock_note1.resolved = False
        
        mock_note2 = Mock()
        mock_note2.id = 2
        mock_note2.body = "Short note"
        mock_note2.created_at = "2024-01-02T00:00:00Z"
        mock_note2.updated_at = "2024-01-02T00:00:00Z"
        mock_note2.author = {"username": "user2", "name": "User 2"}
        mock_note2.system = False
        mock_note2.noteable_type = "MergeRequest"
        mock_note2.noteable_iid = 1
        mock_note2.resolvable = True
        mock_note2.resolved = False
        
        mock_response = mock_paginated_response([mock_note1, mock_note2], total=2)
        mock_mr.notes.list.return_value = mock_response
        mock_project.mergerequests.get.return_value = mock_mr
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_merge_request_notes(
            "project-id", 1, per_page=10, page=1, 
            sort="asc", order_by="created_at", max_body_length=500
        )
        
        # Check that long body was truncated
        assert len(result["notes"][0]["body"]) <= 517  # 500 + "... [truncated]"
        assert result["notes"][0]["body"].endswith("... [truncated]")
        assert result["notes"][0]["truncated"] is True
        
        # Check that short body was not truncated
        assert result["notes"][1]["body"] == "Short note"
        assert "truncated" not in result["notes"][1]
        
        # Check merge request info
        assert result["merge_request"]["iid"] == 1
        assert result["merge_request"]["title"] == "Test MR"
    
    @pytest.mark.unit
    def test_get_branches(self, client):
        """Test getting branches list"""
        mock_project = Mock()
        mock_branch1 = Mock()
        mock_branch1.name = "main"
        mock_branch1.merged = False
        mock_branch1.protected = True
        mock_branch1.default = True
        mock_branch1.web_url = "https://gitlab.com/group/project/-/tree/main"
        
        mock_branch2 = Mock()
        mock_branch2.name = "develop"
        mock_branch2.merged = False
        mock_branch2.protected = False
        mock_branch2.default = False
        mock_branch2.web_url = "https://gitlab.com/group/project/-/tree/develop"
        
        mock_project.branches.list.return_value = [mock_branch1, mock_branch2]
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_branches("project-id")
        
        assert len(result) == 2
        assert result[0]["name"] == "main"
        assert result[0]["protected"] is True
        assert result[0]["default"] is True
    
    @pytest.mark.unit
    def test_get_pipelines(self, client):
        """Test getting pipelines list"""
        mock_project = Mock()
        mock_pipeline1 = Mock()
        mock_pipeline1.id = 1
        mock_pipeline1.status = "success"
        mock_pipeline1.ref = "main"
        mock_pipeline1.sha = "abc123"
        mock_pipeline1.created_at = "2024-01-01T00:00:00Z"
        mock_pipeline1.updated_at = "2024-01-01T00:00:00Z"
        mock_pipeline1.web_url = "https://gitlab.com/group/project/-/pipelines/1"
        
        mock_pipeline2 = Mock()
        mock_pipeline2.id = 2
        mock_pipeline2.status = "failed"
        mock_pipeline2.ref = "main"
        mock_pipeline2.sha = "def456"
        mock_pipeline2.created_at = "2024-01-02T00:00:00Z"
        mock_pipeline2.updated_at = "2024-01-02T00:00:00Z"
        mock_pipeline2.web_url = "https://gitlab.com/group/project/-/pipelines/2"
        
        mock_project.pipelines.list.return_value = [mock_pipeline1, mock_pipeline2]
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_pipelines("project-id", ref="main")
        
        mock_project.pipelines.list.assert_called_once_with(
            ref="main",
            get_all=False,
            per_page=20
        )
        
        assert len(result) == 2
        assert result[0]["status"] == "success"
        assert result[0]["id"] == 1
        assert result[0]["ref"] == "main"
    
    @pytest.mark.unit
    def test_get_file_content(self, client):
        """Test getting file content"""
        import base64
        mock_project = Mock()
        mock_file = Mock()
        # Mock base64 encoded content
        encoded_content = base64.b64encode(b"file content").decode('utf-8')
        mock_file.content = encoded_content
        mock_file.size = 12
        mock_file.encoding = "base64"
        mock_file.last_commit_id = "abc123"
        mock_file.blob_id = "blob456"
        
        mock_project.files.get.return_value = mock_file
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_file_content("project-id", "src/test.py", "main")
        
        mock_project.files.get.assert_called_once_with(
            file_path="src/test.py",
            ref="main"
        )
        
        assert result["content"] == "file content"
        assert result["file_path"] == "src/test.py"
        assert result["size"] == 12
        assert result["encoding"] == "base64"
        assert result["ref"] == "main"
        assert result["last_commit_id"] == "abc123"
    
    @pytest.mark.unit
    def test_search_projects(self, client):
        """Test searching projects globally"""
        mock_project1 = Mock()
        mock_project1.id = 1
        mock_project1.name = "Found 1"
        mock_project1.path = "found-1"
        mock_project1.path_with_namespace = "group/found-1"
        mock_project1.description = "First found project"
        mock_project1.web_url = "https://gitlab.com/group/found-1"
        mock_project1.visibility = "public"
        mock_project1.last_activity_at = "2024-01-01T00:00:00Z"
        
        mock_project2 = Mock()
        mock_project2.id = 2
        mock_project2.name = "Found 2"
        mock_project2.path = "found-2"
        mock_project2.path_with_namespace = "group/found-2"
        mock_project2.description = "Second found project"
        mock_project2.web_url = "https://gitlab.com/group/found-2"
        mock_project2.visibility = "private"
        mock_project2.last_activity_at = "2024-01-02T00:00:00Z"
        
        mock_response = mock_paginated_response([mock_project1, mock_project2], total=2)
        client.gl.projects.list.return_value = mock_response
        
        result = client.search_projects("search-term", per_page=15, page=1)
        
        client.gl.projects.list.assert_called_once_with(
            search="search-term",
            get_all=False,
            per_page=15,
            page=1
        )
        
        assert "projects" in result
        assert len(result["projects"]) == 2
        assert result["projects"][0]["name"] == "Found 1"
        assert result["projects"][1]["name"] == "Found 2"
        assert result["search_term"] == "search-term"
    
    @pytest.mark.unit
    @patch('mcp_gitlab.gitlab_client.GitDetector')
    def test_get_project_from_git(self, mock_detector, client):
        """Test getting project from git repository"""
        # Mock git detection
        mock_detector.detect_gitlab_project.return_value = {
            "host": "gitlab.com",
            "path": "group/project",
            "url": "https://gitlab.com/group/project.git",
            "branch": "feature-branch"
        }
        mock_detector.is_gitlab_url.return_value = True
        
        # Mock project retrieval
        mock_project = Mock()
        mock_project.id = 123
        mock_project.name = "Project"
        mock_project.path = "project"
        mock_project.path_with_namespace = "group/project"
        mock_project.description = "Test project"
        mock_project.web_url = "https://gitlab.com/group/project"
        mock_project.visibility = "private"
        mock_project.last_activity_at = "2024-01-01T00:00:00Z"
        
        client.gl.projects.get.return_value = mock_project
        
        result = client.get_project_from_git(".")
        
        mock_detector.detect_gitlab_project.assert_called_once_with(".")
        client.gl.projects.get.assert_called_once_with("group/project")
        
        assert result["id"] == 123
        assert result["git_info"]["current_branch"] == "feature-branch"
        assert result["git_info"]["detected_from"] == "."
    
    @pytest.mark.unit
    @patch('mcp_gitlab.gitlab_client.GitDetector')
    def test_get_project_from_git_no_detection(self, mock_detector, client):
        """Test getting project from git when no GitLab project detected"""
        mock_detector.detect_gitlab_project.return_value = None
        
        result = client.get_project_from_git(".")
        
        assert result is None
        mock_detector.detect_gitlab_project.assert_called_once_with(".")
    
    @pytest.mark.unit
    def test_get_user_events(self, client):
        """Test getting user events"""
        # Mock the get_user_by_username response
        mock_user_data = {
            "id": 123,
            "username": "testuser",
            "name": "Test User",
            "state": "active",
            "avatar_url": "https://example.com/avatar.png",
            "web_url": "https://gitlab.com/testuser"
        }
        client.get_user_by_username = Mock(return_value=mock_user_data)
        
        # Mock user object for events
        mock_user_obj = Mock()
        mock_event1 = Mock()
        mock_event1.id = 1
        mock_event1.title = "Push event"
        mock_event1.project_id = 456
        mock_event1.action_name = "pushed"
        mock_event1.target_id = None
        mock_event1.target_type = None
        mock_event1.target_title = None
        mock_event1.created_at = "2024-01-01T12:00:00Z"
        mock_event1.author_id = 123
        mock_event1.author_username = "testuser"
        
        mock_event2 = Mock()
        mock_event2.id = 2
        mock_event2.title = "Comment event"
        mock_event2.project_id = 456
        mock_event2.action_name = "commented"
        mock_event2.target_id = 789
        mock_event2.target_type = "Issue"
        mock_event2.target_title = "Test issue"
        mock_event2.created_at = "2024-01-01T11:00:00Z"
        mock_event2.author_id = 123
        mock_event2.author_username = "testuser"
        
        mock_response = mock_paginated_response([mock_event1, mock_event2], total=2)
        mock_user_obj.events.list.return_value = mock_response
        client.gl.users.get.return_value = mock_user_obj
        
        result = client.get_user_events(
            "testuser", 
            action="pushed",
            target_type="Issue",
            per_page=25,
            page=1
        )
        
        client.get_user_by_username.assert_called_once_with("testuser")
        client.gl.users.get.assert_called_once_with(123)
        mock_user_obj.events.list.assert_called_once_with(
            get_all=False,
            per_page=25,
            page=1,
            action="pushed",
            target_type="Issue"
        )
        
        assert "events" in result
        assert len(result["events"]) == 2
        assert result["events"][0]["action_name"] == "pushed"
        assert result["user"]["username"] == "testuser"
    
    @pytest.mark.unit
    def test_get_current_user(self, client):
        """Test getting current authenticated user"""
        # Mock user object with attributes
        mock_user = Mock()
        mock_user.id = 123
        mock_user.username = "johndoe"
        mock_user.name = "John Doe"
        mock_user.email = "john@example.com"
        mock_user.state = "active"
        mock_user.avatar_url = "https://gitlab.com/avatar.jpg"
        mock_user.web_url = "https://gitlab.com/johndoe"
        mock_user.created_at = "2020-01-01T00:00:00Z"
        mock_user.bio = "Software Developer"
        mock_user.organization = "ACME Corp"
        mock_user.job_title = "Senior Developer"
        mock_user.public_email = "john@example.com"
        mock_user.is_admin = False
        mock_user.can_create_group = True
        mock_user.can_create_project = True
        mock_user.two_factor_enabled = True
        mock_user.external = False
        
        client.gl.user = mock_user
        
        result = client.get_current_user()
        
        assert result["id"] == 123
        assert result["username"] == "johndoe"
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["is_admin"] is False
        assert result["two_factor_enabled"] is True
    
    @pytest.mark.unit
    def test_get_user_by_id(self, client):
        """Test getting user by ID"""
        mock_user = Mock()
        mock_user.id = 456
        mock_user.username = "janedoe"
        mock_user.name = "Jane Doe"
        mock_user.state = "active"
        mock_user.avatar_url = "https://gitlab.com/avatar2.jpg"
        mock_user.web_url = "https://gitlab.com/janedoe"
        mock_user.created_at = "2021-01-01T00:00:00Z"
        mock_user.bio = "Product Manager"
        mock_user.organization = "Tech Inc"
        mock_user.job_title = "PM"
        mock_user.public_email = "jane@example.com"
        mock_user.external = False
        
        client.gl.users.get.return_value = mock_user
        
        result = client.get_user(user_id=456)
        
        assert result["id"] == 456
        assert result["username"] == "janedoe"
        assert result["name"] == "Jane Doe"
        client.gl.users.get.assert_called_once_with(456)
    
    @pytest.mark.unit
    def test_get_user_by_username(self, client):
        """Test getting user by username"""
        mock_user = Mock()
        mock_user.id = 789
        mock_user.username = "testuser"
        mock_user.name = "Test User"
        mock_user.state = "active"
        mock_user.avatar_url = None
        mock_user.web_url = "https://gitlab.com/testuser"
        
        # Mock get_user_by_username
        client.get_user_by_username = Mock(return_value={
            "id": 789,
            "username": "testuser",
            "name": "Test User",
            "state": "active",
            "avatar_url": None,
            "web_url": "https://gitlab.com/testuser"
        })
        
        result = client.get_user(username="testuser")
        
        assert result["id"] == 789
        assert result["username"] == "testuser"
        client.get_user_by_username.assert_called_once_with("testuser")
    
    @pytest.mark.unit
    def test_get_user_not_found(self, client):
        """Test getting user returns None when not found"""
        client.gl.users.get.side_effect = gitlab.exceptions.GitlabGetError()
        
        result = client.get_user(user_id=999)
        
        assert result is None
    
    @pytest.mark.unit
    def test_get_user_no_params(self, client):
        """Test get_user raises error when no params provided"""
        with pytest.raises(ValueError, match="Either user_id or username must be provided"):
            client.get_user()