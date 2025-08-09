import os
import re
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class GitDetector:
    """Detect and parse GitLab project information from git repositories using file-based approach"""
    
    @staticmethod
    def is_git_repository(path: str = ".") -> bool:
        """Check if the given path is inside a git repository by looking for .git directory"""
        # Validate and sanitize path to prevent directory traversal
        try:
            path = os.path.abspath(os.path.expanduser(path))
            if not os.path.exists(path):
                return False
            if not os.path.isdir(path):
                return False
        except (ValueError, OSError):
            return False
        
        # Check for .git directory
        git_dir = os.path.join(path, ".git")
        if os.path.isdir(git_dir):
            return True
        
        # Check if we're in a subdirectory of a git repository
        current = path
        while current != os.path.dirname(current):  # While not at root
            git_dir = os.path.join(current, ".git")
            if os.path.isdir(git_dir):
                return True
            current = os.path.dirname(current)
        
        return False
    
    @staticmethod
    def find_git_directory(path: str = ".") -> Optional[str]:
        """Find the .git directory for the given path"""
        # Validate path
        try:
            path = os.path.abspath(os.path.expanduser(path))
            if not os.path.exists(path) or not os.path.isdir(path):
                return None
        except (ValueError, OSError):
            return None
        
        # Check current directory first
        git_dir = os.path.join(path, ".git")
        if os.path.isdir(git_dir):
            return git_dir
        
        # Check parent directories
        current = path
        while current != os.path.dirname(current):
            git_dir = os.path.join(current, ".git")
            if os.path.isdir(git_dir):
                return git_dir
            current = os.path.dirname(current)
        
        return None
    
    @staticmethod
    def parse_git_config(config_content: str) -> Dict[str, Dict[str, str]]:
        """Parse git config file content into a dictionary"""
        config = {}
        current_section = None
        
        for line in config_content.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Section header [section "name"]
            section_match = re.match(r'\[([^\s]+)(?:\s+"([^"]+)")?\]', line)
            if section_match:
                section_type = section_match.group(1)
                section_name = section_match.group(2) or ""
                current_section = f"{section_type}:{section_name}" if section_name else section_type
                config[current_section] = {}
                continue
            
            # Key-value pair
            if current_section and '=' in line:
                key, value = line.split('=', 1)
                config[current_section][key.strip()] = value.strip()
        
        return config
    
    @staticmethod
    def get_remote_urls(path: str = ".") -> Dict[str, str]:
        """Get all git remote URLs by reading .git/config file"""
        git_dir = GitDetector.find_git_directory(path)
        if not git_dir:
            return {}
        
        config_file = os.path.join(git_dir, "config")
        if not os.path.isfile(config_file):
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            config = GitDetector.parse_git_config(config_content)
            remotes = {}
            
            # Find all remote sections
            for section_name, section_data in config.items():
                if section_name.startswith("remote:"):
                    remote_name = section_name.split(":", 1)[1]
                    if "url" in section_data:
                        remotes[remote_name] = section_data["url"]
            
            return remotes
        except (IOError, OSError) as e:
            logger.debug(f"Failed to read git config: {e}")
            return {}
    
    @staticmethod
    def get_current_branch(path: str = ".") -> Optional[str]:
        """Get the current git branch name by reading .git/HEAD"""
        git_dir = GitDetector.find_git_directory(path)
        if not git_dir:
            return None
        
        head_file = os.path.join(git_dir, "HEAD")
        if not os.path.isfile(head_file):
            return None
        
        try:
            with open(head_file, 'r', encoding='utf-8') as f:
                head_content = f.read().strip()
            
            # HEAD can be either a ref or a commit hash
            if head_content.startswith("ref: refs/heads/"):
                return head_content.replace("ref: refs/heads/", "")
            else:
                # Detached HEAD state - return None or the commit hash
                return None
        except (IOError, OSError) as e:
            logger.debug(f"Failed to read HEAD file: {e}")
            return None
    
    @staticmethod
    def parse_gitlab_url(url: str) -> Optional[Dict[str, Any]]:
        """Parse a GitLab URL and extract project information
        
        Supports formats:
        - https://gitlab.com/group/project.git
        - https://gitlab.com/group/subgroup/project
        - git@gitlab.com:group/project.git
        - ssh://git@gitlab.com/group/project.git
        """
        try:
            # Handle SSH URLs
            if url.startswith("git@"):
                # Convert git@host:path to ssh://git@host/path
                parts = url.split(":", 1)
                if len(parts) == 2:
                    host_part = parts[0]
                    path_part = parts[1]
                    url = f"ssh://{host_part}/{path_part}"
            
            parsed = urlparse(url)
            
            # Extract host
            host = parsed.hostname or parsed.netloc.split("@")[-1].split(":")[0]
            if not host:
                return None
            
            # Extract path and clean it
            path = parsed.path
            if not path or path == "/":
                # For SSH URLs like git@host:path
                if ":" in url and not url.startswith("ssh://"):
                    path = url.split(":", 1)[1]
                else:
                    return None
            
            # Remove leading slash and .git suffix
            path = path.strip("/")
            if path.endswith(".git"):
                path = path[:-4]
            
            # Split into namespace and project
            path_parts = path.split("/")
            if len(path_parts) < 2:
                return None
            
            project_name = path_parts[-1]
            namespace = "/".join(path_parts[:-1])
            
            return {
                "host": host,
                "namespace": namespace,
                "project": project_name,
                "path": path,
                "url": url
            }
            
        except Exception as e:
            logger.debug(f"Failed to parse GitLab URL '{url}': {e}")
            return None
    
    @classmethod
    def detect_gitlab_project(cls, path: str = ".", preferred_remote: str = "origin") -> Optional[Dict[str, Any]]:
        """Detect GitLab project from git repository
        
        Returns:
            Dictionary with project information or None if not found
            {
                "host": "gitlab.com",
                "namespace": "group/subgroup", 
                "project": "project-name",
                "path": "group/subgroup/project-name",
                "url": "original-remote-url",
                "branch": "current-branch"
            }
        """
        if not cls.is_git_repository(path):
            return None
        
        remotes = cls.get_remote_urls(path)
        if not remotes:
            return None
        
        # Try preferred remote first
        if preferred_remote in remotes:
            parsed = cls.parse_gitlab_url(remotes[preferred_remote])
            if parsed:
                parsed["branch"] = cls.get_current_branch(path)
                return parsed
        
        # Try other remotes
        for remote_name, remote_url in remotes.items():
            parsed = cls.parse_gitlab_url(remote_url)
            if parsed:
                parsed["branch"] = cls.get_current_branch(path)
                return parsed
        
        return None
    
    @classmethod
    def is_gitlab_url(cls, url: str, gitlab_host: Optional[str] = None) -> bool:
        """Check if a URL is a GitLab URL.

        Args:
            url: The URL to check.
            gitlab_host: If provided, the URL must match this specific GitLab
                host. When not provided, the hostname must either be
                ``gitlab.com``, a subdomain of ``gitlab.com``, or include a
                distinct ``gitlab`` label (e.g., ``gitlab.example.com``).
        """
        parsed = cls.parse_gitlab_url(url)
        if not parsed:
            return False
        
        if gitlab_host:
            # Normalize hosts for comparison
            url_host = parsed["host"].lower().replace("www.", "")
            check_host = (
                gitlab_host.lower()
                .replace("www.", "")
                .replace("https://", "")
                .replace("http://", "")
                .split("/")[0]
            )
            return url_host == check_host

        # Default behavior: ensure the URL points to a GitLab host using
        # common hostname patterns. We explicitly allow:
        #   - gitlab.com and any subdomain of gitlab.com
        #   - self-hosted instances whose hostname contains a distinct
        #     ``gitlab`` label (e.g., ``gitlab.example.com`` or
        #     ``sub.gitlab.example.org``)
        host = parsed["host"].lower()

        # Official GitLab SaaS domain
        if host == "gitlab.com" or host.endswith(".gitlab.com"):
            return True

        # Self-hosted GitLab instances: look for a '.gitlab.' label or a
        # hostname starting with 'gitlab.'
        if host.startswith("gitlab.") or ".gitlab." in host:
            return True

        return False
