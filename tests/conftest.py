"""Shared test fixtures and configuration

This file also provides lightweight stub implementations of optional
dependencies so that the test suite can run in environments where the real
packages (``python-gitlab`` and ``mcp``) are not installed. The production
code only touches a very small portion of these libraries in unit tests, so
simple placeholder objects are sufficient. If the real packages are
available they will be used instead and these stubs have no effect.
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
import types
import sys

# ---------------------------------------------------------------------------
# Optional dependency stubs
# ---------------------------------------------------------------------------

# Provide a minimal stub for the ``gitlab`` package if it's missing.  The
# handlers and client only require that ``gitlab.Gitlab`` exists so tests can
# patch it, as well as modules for ``gitlab.exceptions`` and
# ``gitlab.v4.objects`` with placeholder classes.
if "gitlab" not in sys.modules:
    gitlab_module = types.ModuleType("gitlab")
    exceptions_module = types.ModuleType("gitlab.exceptions")
    v4_module = types.ModuleType("gitlab.v4")
    objects_module = types.ModuleType("gitlab.v4.objects")

    # Basic placeholder classes used in type hints or patched in tests
    class Gitlab:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    class Project:  # pragma: no cover - simple stub
        pass

    class Issue:  # pragma: no cover - simple stub
        pass

    class MergeRequest:  # pragma: no cover - simple stub
        pass

    gitlab_module.Gitlab = Gitlab
    gitlab_module.exceptions = exceptions_module
    gitlab_module.v4 = v4_module
    v4_module.objects = objects_module
    objects_module.Project = Project
    objects_module.Issue = Issue
    objects_module.MergeRequest = MergeRequest

    # Common exception classes referenced in the code/tests
    class GitlabError(Exception):
        pass

    class GitlabGetError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabAuthenticationError(GitlabError):
        pass

    class GitlabHttpError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabListError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabCreateError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabUpdateError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabDeleteError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    exceptions_module.GitlabError = GitlabError
    exceptions_module.GitlabGetError = GitlabGetError
    exceptions_module.GitlabAuthenticationError = GitlabAuthenticationError
    exceptions_module.GitlabHttpError = GitlabHttpError
    exceptions_module.GitlabListError = GitlabListError
    exceptions_module.GitlabCreateError = GitlabCreateError
    exceptions_module.GitlabUpdateError = GitlabUpdateError
    exceptions_module.GitlabDeleteError = GitlabDeleteError

    sys.modules["gitlab"] = gitlab_module
    sys.modules["gitlab.exceptions"] = exceptions_module
    sys.modules["gitlab.v4"] = v4_module
    sys.modules["gitlab.v4.objects"] = objects_module

# Provide a minimal stub for the ``mcp`` package when it's not installed.
# Only a handful of classes/functions are required for the tests.
if "mcp" not in sys.modules:
    mcp_module = types.ModuleType("mcp")
    server_module = types.ModuleType("mcp.server")
    models_module = types.ModuleType("mcp.server.models")
    stdio_module = types.ModuleType("mcp.server.stdio")
    types_module = types.ModuleType("mcp.types")

    class Server:  # pragma: no cover - simple stub
        """Very small stand-in for mcp.server.Server used in tests.

        It only implements the decorator methods utilized by the server
        module. The decorators simply return the wrapped function unchanged.
        """

        def __init__(self, *args, **kwargs):
            pass

        def list_tools(self):  # pragma: no cover - simple stub
            def decorator(func):
                return func
            return decorator

        def call_tool(self):  # pragma: no cover - simple stub
            def decorator(func):
                return func
            return decorator

        def get_capabilities(self, *args, **kwargs):  # pragma: no cover - stub
            return {}

        async def run(self, *args, **kwargs):  # pragma: no cover - stub
            return None

    class NotificationOptions:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    class InitializationOptions:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    def stdio_server(*args, **kwargs):  # pragma: no cover - simple stub
        pass

    # Simple classes used for responses in the server module
    class Tool:  # pragma: no cover - simple stub
        def __init__(self, name: str, description: str = "", inputSchema: dict | None = None):
            self.name = name
            self.description = description
            self.inputSchema = inputSchema

    class TextContent:  # pragma: no cover - simple stub
        def __init__(self, type: str = "text", text: str = ""):
            self.type = type
            self.text = text

    class ImageContent:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    class EmbeddedResource:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    server_module.Server = Server
    server_module.NotificationOptions = NotificationOptions
    stdio_module.stdio_server = stdio_server
    models_module.InitializationOptions = InitializationOptions

    types_module.Tool = Tool
    types_module.TextContent = TextContent
    types_module.ImageContent = ImageContent
    types_module.EmbeddedResource = EmbeddedResource

    mcp_module.server = server_module
    mcp_module.types = types_module

    sys.modules["mcp"] = mcp_module
    sys.modules["mcp.server"] = server_module
    sys.modules["mcp.server.models"] = models_module
    sys.modules["mcp.server.stdio"] = stdio_module
    sys.modules["mcp.types"] = types_module

# Provide extremely small pydantic stand-ins when the library isn't
# available.  They only implement the pieces required for test execution.
if "pydantic" not in sys.modules:
    pydantic_module = types.ModuleType("pydantic")

    class BaseModel:  # pragma: no cover - simple stub
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(default=None, **kwargs):  # pragma: no cover - simple stub
        return default

    class AnyUrl(str):  # pragma: no cover - simple stub
        pass

    pydantic_module.BaseModel = BaseModel
    pydantic_module.Field = Field
    pydantic_module.AnyUrl = AnyUrl

    sys.modules["pydantic"] = pydantic_module

# Minimal stub for python-dotenv when not installed.
if "dotenv" not in sys.modules:
    dotenv_module = types.ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):  # pragma: no cover - simple stub
        return None

    dotenv_module.load_dotenv = load_dotenv
    sys.modules["dotenv"] = dotenv_module


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


# ---------------------------------------------------------------------------
# Asyncio test support
# ---------------------------------------------------------------------------
import asyncio


def pytest_configure(config):  # pragma: no cover - test harness setup
    config.addinivalue_line("markers", "asyncio: mark test to run on event loop")


import inspect


@pytest.hookimpl()
def pytest_pyfunc_call(pyfuncitem):  # pragma: no cover - test harness setup
    if pyfuncitem.get_closest_marker("asyncio"):
        func = pyfuncitem.obj
        params = inspect.signature(func).parameters
        kwargs = {name: pyfuncitem.funcargs[name] for name in params}
        asyncio.run(func(**kwargs))
        return True
    return None