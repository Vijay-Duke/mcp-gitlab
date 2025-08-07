"""Shared test fixtures and configuration"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch

# Test constants
TEST_USER_NAME = "Test User"
TEST_USERNAME = "testuser"
TEST_GROUP = "test-group"
TEST_PROJECT = "test-project"


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repository structure"""
    # Create .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    
    # Create config file
    config_file = git_dir / "config"
    config_content = """
[core]
    repositoryformatversion = 0
    filemode = true
[remote "origin"]
    url = https://gitlab.com/test-group/test-project.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
    remote = origin
    merge = refs/heads/main
"""
    config_file.write_text(config_content)
    
    # Create HEAD file
    head_file = git_dir / "HEAD"
    head_file.write_text("ref: refs/heads/main\n")
    
    return tmp_path


@pytest.fixture
def mock_gitlab_config():
    """Create a mock GitLab configuration"""
    from mcp_gitlab.gitlab_client import GitLabConfig
    return GitLabConfig(
        url="https://gitlab.com",
        private_token="test-token-12345"
    )


@pytest.fixture
def mock_project_data():
    """Mock GitLab project data"""
    return {
        "id": 123,
        "name": "Test Project",
        "description": "A test project for unit tests",
        "path": "test-project",
        "path_with_namespace": "test-group/test-project",
        "web_url": "https://gitlab.com/test-group/test-project",
        "default_branch": "main",
        "visibility": "private",
        "created_at": "2024-01-01T00:00:00Z",
        "last_activity_at": "2024-01-15T12:00:00Z"
    }


@pytest.fixture
def mock_issue_data():
    """Mock GitLab issue data"""
    return [
        {
            "iid": 1,
            "title": "First Issue",
            "description": "This is the first issue",
            "state": "opened",
            "created_at": "2024-01-01T10:00:00Z",
            "author": {"name": TEST_USER_NAME, "username": TEST_USERNAME},
            "labels": ["bug", "priority::high"]
        },
        {
            "iid": 2,
            "title": "Second Issue",
            "description": "This is the second issue",
            "state": "closed",
            "created_at": "2024-01-02T10:00:00Z",
            "author": {"name": "Another User", "username": "anotheruser"},
            "labels": ["feature"]
        }
    ]


@pytest.fixture
def mock_merge_request_data():
    """Mock GitLab merge request data"""
    return [
        {
            "iid": 10,
            "title": "Feature: Add new functionality",
            "description": "This MR adds new functionality",
            "state": "opened",
            "source_branch": "feature-branch",
            "target_branch": "main",
            "author": {"name": "Developer", "username": "dev"},
            "created_at": "2024-01-10T14:00:00Z",
            "merge_status": "can_be_merged"
        },
        {
            "iid": 11,
            "title": "Fix: Resolve bug in module",
            "description": "This MR fixes a critical bug",
            "state": "merged",
            "source_branch": "bugfix-branch",
            "target_branch": "main",
            "author": {"name": "Developer", "username": "dev"},
            "created_at": "2024-01-11T14:00:00Z",
            "merged_at": "2024-01-11T16:00:00Z",
            "merge_status": "merged"
        }
    ]


@pytest.fixture
def mock_commit_data():
    """Mock GitLab commit data"""
    return [
        {
            "id": "abc123def456",
            "short_id": "abc123d",
            "title": "Add new feature",
            "message": "Add new feature\n\nThis commit adds a new feature to the project",
            "author_name": "Test Developer",
            "author_email": "dev@example.com",
            "created_at": "2024-01-15T10:00:00Z",
            "parent_ids": ["xyz789fed321"]
        },
        {
            "id": "xyz789fed321",
            "short_id": "xyz789f",
            "title": "Initial commit",
            "message": "Initial commit",
            "author_name": "Test Developer",
            "author_email": "dev@example.com",
            "created_at": "2024-01-01T09:00:00Z",
            "parent_ids": []
        }
    ]


@pytest.fixture
def mock_file_tree_data():
    """Mock GitLab repository tree data"""
    return [
        {
            "id": "tree1",
            "name": "src",
            "type": "tree",
            "path": "src",
            "mode": "040000"
        },
        {
            "id": "file1",
            "name": "README.md",
            "type": "blob",
            "path": "README.md",
            "mode": "100644"
        },
        {
            "id": "file2",
            "name": ".gitignore",
            "type": "blob",
            "path": ".gitignore",
            "mode": "100644"
        }
    ]


@pytest.fixture
def mock_pipeline_data():
    """Mock GitLab pipeline data"""
    return [
        {
            "id": 1001,
            "status": "success",
            "ref": "main",
            "sha": "abc123def456",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:45:00Z",
            "web_url": "https://gitlab.com/test-group/test-project/-/pipelines/1001"
        },
        {
            "id": 1002,
            "status": "failed",
            "ref": "feature-branch",
            "sha": "def456ghi789",
            "created_at": "2024-01-15T11:00:00Z",
            "updated_at": "2024-01-15T11:10:00Z",
            "web_url": "https://gitlab.com/test-group/test-project/-/pipelines/1002"
        }
    ]


@pytest.fixture
def mock_user_events_data():
    """Mock GitLab user events data"""
    return [
        {
            "id": 1,
            "action_name": "pushed",
            "created_at": "2024-01-15T10:00:00Z",
            "author": {"name": TEST_USER_NAME, "username": TEST_USERNAME},
            "push_data": {
                "commit_count": 1,
                "ref": "main",
                "commit_title": "Update README"
            }
        },
        {
            "id": 2,
            "action_name": "commented",
            "created_at": "2024-01-15T09:00:00Z",
            "author": {"name": TEST_USER_NAME, "username": TEST_USERNAME},
            "note": {
                "body": "This looks good!",
                "noteable_type": "MergeRequest",
                "noteable_iid": 10
            }
        }
    ]


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    from mcp_gitlab.utils import GitLabClientManager
    GitLabClientManager._instance = None
    yield
    GitLabClientManager._instance = None


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv("GITLAB_URL", "https://gitlab.example.com")
    monkeypatch.setenv("GITLAB_PRIVATE_TOKEN", "test-token-env")
    monkeypatch.setenv("GITLAB_DEFAULT_PAGE_SIZE", "25")
    monkeypatch.setenv("GITLAB_LOG_LEVEL", "DEBUG")