"""Integration tests for MCP GitLab server

These tests require a GitLab instance and are marked as integration tests.
They will be skipped in CI unless proper credentials are provided.
"""
import pytest
import os
from mcp_gitlab.gitlab_client import GitLabClient, GitLabConfig
from mcp_gitlab.git_detector import GitDetector


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GITLAB_PRIVATE_TOKEN"),
    reason="No GitLab token provided for integration tests"
)
class TestGitLabIntegration:
    """Integration tests that connect to real GitLab instance"""
    
    @pytest.fixture
    def client(self):
        """Create real GitLab client for integration tests"""
        config = GitLabConfig(
            url=os.getenv("GITLAB_URL", "https://gitlab.com"),
            private_token=os.getenv("GITLAB_PRIVATE_TOKEN")
        )
        return GitLabClient(config)
    
    def test_get_current_user_projects(self, client):
        """Test getting current user's projects"""
        result = client.get_projects(owned=True, per_page=5, page=1)
        
        assert "data" in result
        assert "pagination" in result
        assert isinstance(result["data"], list)
        
        # If user has projects, verify structure
        if result["data"]:
            project = result["data"][0]
            assert "id" in project
            assert "name" in project
            assert "path_with_namespace" in project
    
    def test_search_projects(self, client):
        """Test searching for projects"""
        # Search for a common term
        result = client.search_projects("gitlab", per_page=5, page=1)
        
        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) <= 5  # Respect page size
    
    def test_project_detection_in_git_repo(self, client):
        """Test project detection in actual git repository"""
        # This test assumes it's running inside a git repository
        if GitDetector.is_git_repository():
            detected = client.get_project_from_git()
            
            if detected:
                # If detection worked, verify structure
                assert "id" in detected
                assert "git_info" in detected
                assert "current_branch" in detected["git_info"]
    
    @pytest.mark.skipif(
        not os.getenv("GITLAB_TEST_PROJECT_ID"),
        reason="No test project ID provided"
    )
    def test_project_resources(self, client):
        """Test accessing various project resources"""
        project_id = os.getenv("GITLAB_TEST_PROJECT_ID")
        
        # Test getting project details
        project = client.get_project(project_id)
        assert project is not None
        assert "id" in project
        
        # Test getting issues
        issues = client.get_issues(project_id, state="all", per_page=5, page=1)
        assert "data" in issues
        assert isinstance(issues["data"], list)
        
        # Test getting merge requests
        mrs = client.get_merge_requests(project_id, state="all", per_page=5, page=1)
        assert "data" in mrs
        assert isinstance(mrs["data"], list)
        
        # Test getting branches
        branches = client.get_branches(project_id)
        assert isinstance(branches, list)
        if branches:
            assert "name" in branches[0]