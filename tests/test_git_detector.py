"""Tests for GitDetector class"""
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from mcp_gitlab.git_detector import GitDetector


class TestGitDetector:
    """Test cases for GitDetector class"""
    
    @pytest.mark.unit
    def test_is_git_repository_with_git_dir(self, tmp_path):
        """Test detection of git repository when .git directory exists"""
        # Create a .git directory
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        assert GitDetector.is_git_repository(str(tmp_path)) is True
    
    @pytest.mark.unit
    def test_is_git_repository_without_git_dir(self, tmp_path):
        """Test detection returns False when no .git directory exists"""
        assert GitDetector.is_git_repository(str(tmp_path)) is False
    
    @pytest.mark.unit
    def test_is_git_repository_in_subdirectory(self, tmp_path):
        """Test detection from subdirectory of git repository"""
        # Create git repo structure
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        assert GitDetector.is_git_repository(str(subdir)) is True
    
    @pytest.mark.unit
    def test_find_git_directory(self, tmp_path):
        """Test finding .git directory path"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        result = GitDetector.find_git_directory(str(tmp_path))
        assert result == str(git_dir)
    
    @pytest.mark.unit
    def test_find_git_directory_from_subdirectory(self, tmp_path):
        """Test finding .git directory from subdirectory"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        result = GitDetector.find_git_directory(str(subdir))
        assert result == str(git_dir)
    
    @pytest.mark.unit
    def test_parse_git_config(self):
        """Test parsing git config file content"""
        config_content = """
[core]
    repositoryformatversion = 0
    filemode = true
[remote "origin"]
    url = https://gitlab.com/group/project.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
    remote = origin
    merge = refs/heads/main
"""
        result = GitDetector.parse_git_config(config_content)
        
        assert "core" in result
        assert result["core"]["repositoryformatversion"] == "0"
        assert "remote:origin" in result
        assert result["remote:origin"]["url"] == "https://gitlab.com/group/project.git"
        assert "branch:main" in result
        assert result["branch:main"]["remote"] == "origin"
    
    @pytest.mark.unit
    def test_get_remote_urls(self, tmp_path):
        """Test getting remote URLs from git config"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        config_content = """
[remote "origin"]
    url = https://gitlab.com/group/project.git
[remote "upstream"]
    url = git@gitlab.com:upstream/project.git
"""
        config_file = git_dir / "config"
        config_file.write_text(config_content)
        
        remotes = GitDetector.get_remote_urls(str(tmp_path))
        
        assert remotes["origin"] == "https://gitlab.com/group/project.git"
        assert remotes["upstream"] == "git@gitlab.com:upstream/project.git"
    
    @pytest.mark.unit
    def test_get_current_branch(self, tmp_path):
        """Test getting current branch name"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        # Normal branch
        head_file = git_dir / "HEAD"
        head_file.write_text("ref: refs/heads/feature-branch\n")
        
        branch = GitDetector.get_current_branch(str(tmp_path))
        assert branch == "feature-branch"
    
    @pytest.mark.unit
    def test_get_current_branch_detached_head(self, tmp_path):
        """Test getting branch name in detached HEAD state"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        # Detached HEAD
        head_file = git_dir / "HEAD"
        head_file.write_text("a1b2c3d4e5f6\n")
        
        branch = GitDetector.get_current_branch(str(tmp_path))
        assert branch is None
    
    @pytest.mark.unit
    @pytest.mark.parametrize("url,expected", [
        (
            "https://gitlab.com/group/project.git",
            {
                "host": "gitlab.com",
                "namespace": "group",
                "project": "project",
                "path": "group/project"
            }
        ),
        (
            "git@gitlab.com:group/subgroup/project.git",
            {
                "host": "gitlab.com",
                "namespace": "group/subgroup",
                "project": "project",
                "path": "group/subgroup/project"
            }
        ),
        (
            "ssh://git@gitlab.example.com/namespace/project.git",
            {
                "host": "gitlab.example.com",
                "namespace": "namespace",
                "project": "project",
                "path": "namespace/project"
            }
        ),
        (
            "https://github.com/user/repo.git",
            {
                "host": "github.com",
                "namespace": "user",
                "project": "repo",
                "path": "user/repo"
            }
        )
    ])
    def test_parse_gitlab_url(self, url, expected):
        """Test parsing various GitLab URL formats"""
        result = GitDetector.parse_gitlab_url(url)
        
        assert result is not None
        assert result["host"] == expected["host"]
        assert result["namespace"] == expected["namespace"]
        assert result["project"] == expected["project"]
        assert result["path"] == expected["path"]
        # For SSH URLs starting with git@, they get normalized to ssh:// format
        if url.startswith("git@"):
            expected_url = url.replace(":", "/", 1)
            expected_url = f"ssh://{expected_url}"
            assert result["url"] == expected_url
        else:
            assert result["url"] == url
    
    @pytest.mark.unit
    def test_parse_gitlab_url_invalid(self):
        """Test parsing invalid URLs returns None"""
        invalid_urls = [
            "not-a-url",
            "https://",
            "gitlab.com/project",  # Missing namespace
            ""
        ]
        
        for url in invalid_urls:
            result = GitDetector.parse_gitlab_url(url)
            assert result is None
    
    @pytest.mark.unit
    def test_detect_gitlab_project(self, tmp_path):
        """Test full GitLab project detection"""
        # Set up git repository
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        config_content = """
[remote "origin"]
    url = https://gitlab.com/mygroup/myproject.git
"""
        config_file = git_dir / "config"
        config_file.write_text(config_content)
        
        head_file = git_dir / "HEAD"
        head_file.write_text("ref: refs/heads/main\n")
        
        result = GitDetector.detect_gitlab_project(str(tmp_path))
        
        assert result is not None
        assert result["host"] == "gitlab.com"
        assert result["namespace"] == "mygroup"
        assert result["project"] == "myproject"
        assert result["path"] == "mygroup/myproject"
        assert result["branch"] == "main"
    
    @pytest.mark.unit
    def test_detect_gitlab_project_no_git(self, tmp_path):
        """Test detection returns None when not in git repository"""
        result = GitDetector.detect_gitlab_project(str(tmp_path))
        assert result is None
    
    @pytest.mark.unit
    def test_is_gitlab_url(self):
        """Test checking if URL is a GitLab URL"""
        # Valid GitLab URLs
        assert GitDetector.is_gitlab_url("https://gitlab.com/group/project.git") is True
        assert GitDetector.is_gitlab_url("git@gitlab.com:group/project.git") is True
        
        # Invalid URLs
        assert GitDetector.is_gitlab_url("not-a-url") is False
        assert GitDetector.is_gitlab_url("https://gitlab.com/project") is False
    
    @pytest.mark.unit
    def test_is_gitlab_url_with_host_check(self):
        """Test checking if URL matches specific GitLab host"""
        url = "https://gitlab.com/group/project.git"
        
        # Matching host
        assert GitDetector.is_gitlab_url(url, "gitlab.com") is True
        assert GitDetector.is_gitlab_url(url, "https://gitlab.com") is True
        
        # Non-matching host
        assert GitDetector.is_gitlab_url(url, "github.com") is False
        assert GitDetector.is_gitlab_url(url, "gitlab.example.com") is False