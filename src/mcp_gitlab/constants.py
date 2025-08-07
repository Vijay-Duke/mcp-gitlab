"""
Constants and configuration values for MCP GitLab server
Environment variables can override these defaults with GITLAB_ prefix
"""
import os

# Pagination settings (environment configurable)
DEFAULT_PAGE_SIZE = int(os.getenv("GITLAB_DEFAULT_PAGE_SIZE", "50"))
MAX_PAGE_SIZE = int(os.getenv("GITLAB_MAX_PAGE_SIZE", "100"))
SMALL_PAGE_SIZE = int(os.getenv("GITLAB_SMALL_PAGE_SIZE", "20"))

# Response settings (environment configurable)
DEFAULT_MAX_BODY_LENGTH = int(os.getenv("GITLAB_MAX_BODY_LENGTH", "500"))
MAX_RESPONSE_SIZE = int(os.getenv("GITLAB_MAX_RESPONSE_SIZE", "25000"))  # Maximum characters in a response to avoid token limits

# Cache settings (environment configurable)
CACHE_TTL_SHORT = int(os.getenv("GITLAB_CACHE_TTL_SHORT", "60"))  # 1 minute for rapidly changing data
CACHE_TTL_MEDIUM = int(os.getenv("GITLAB_CACHE_TTL_MEDIUM", "300"))  # 5 minutes for moderately changing data  
CACHE_TTL_LONG = int(os.getenv("GITLAB_CACHE_TTL_LONG", "3600"))  # 1 hour for rarely changing data
CACHE_MAX_SIZE = int(os.getenv("GITLAB_CACHE_MAX_SIZE", "128"))  # Maximum number of cached items

# Retry settings (environment configurable)
MAX_RETRIES = int(os.getenv("GITLAB_MAX_RETRIES", "3"))
RETRY_DELAY_BASE = float(os.getenv("GITLAB_RETRY_DELAY_BASE", "1.0"))  # Base delay in seconds
RETRY_BACKOFF_FACTOR = float(os.getenv("GITLAB_RETRY_BACKOFF_FACTOR", "2.0"))  # Exponential backoff multiplier
MAX_RETRY_DELAY = float(os.getenv("GITLAB_MAX_RETRY_DELAY", "30.0"))  # Maximum delay between retries

# API settings (environment configurable)
DEFAULT_GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
CONNECTION_TIMEOUT = int(os.getenv("GITLAB_CONNECTION_TIMEOUT", "30"))  # Seconds
READ_TIMEOUT = int(os.getenv("GITLAB_READ_TIMEOUT", "60"))  # Seconds

# Git detection settings (environment configurable)
DEFAULT_REMOTE_NAME = os.getenv("GITLAB_DEFAULT_REMOTE", "origin")
GIT_CONFIG_ENCODING = os.getenv("GITLAB_GIT_ENCODING", "utf-8")

# Logging settings (environment configurable)
LOG_LEVEL = os.getenv("GITLAB_LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("GITLAB_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
JSON_LOGGING = os.getenv("GITLAB_JSON_LOGGING", "false").lower() == "true"

# Error messages (environment configurable)
ERROR_NO_TOKEN = os.getenv("GITLAB_ERROR_NO_TOKEN", "No GitLab authentication token found. Please set GITLAB_PRIVATE_TOKEN or GITLAB_OAUTH_TOKEN.")
ERROR_AUTH_FAILED = os.getenv("GITLAB_ERROR_AUTH_FAILED", "Authentication failed. Please check your GitLab token.")
ERROR_NOT_FOUND = os.getenv("GITLAB_ERROR_NOT_FOUND", "The requested resource was not found.")
ERROR_RATE_LIMIT = os.getenv("GITLAB_ERROR_RATE_LIMIT", "Rate limit exceeded. Please try again later.")
ERROR_GENERIC = os.getenv("GITLAB_ERROR_GENERIC", "An unexpected error occurred. Please try again.")
ERROR_NO_PROJECT = os.getenv("GITLAB_ERROR_NO_PROJECT", "No GitLab project detected in the current directory.")
ERROR_INVALID_INPUT = os.getenv("GITLAB_ERROR_INVALID_INPUT", "Invalid input provided. Please check the parameters.")

# Tool names (for consistency)
TOOL_LIST_PROJECTS = "gitlab_list_projects"
TOOL_GET_PROJECT = "gitlab_get_project"
TOOL_LIST_ISSUES = "gitlab_list_issues"
TOOL_CREATE_ISSUE = "gitlab_create_issue"
TOOL_LIST_MRS = "gitlab_list_merge_requests"
TOOL_CREATE_MR = "gitlab_create_merge_request"
TOOL_LIST_PIPELINES = "gitlab_list_pipelines"
TOOL_LIST_BRANCHES = "gitlab_list_branches"
TOOL_DETECT_PROJECT = "gitlab_detect_project"  # Deprecated, use TOOL_GET_CURRENT_PROJECT
TOOL_GET_CURRENT_PROJECT = "gitlab_get_current_project"
TOOL_GET_MR_NOTES = "gitlab_get_merge_request_notes"
TOOL_GET_USER_EVENTS = "gitlab_get_user_events"

# New renamed tools
TOOL_LIST_COMMITS = "gitlab_list_commits"
TOOL_LIST_REPOSITORY_TREE = "gitlab_list_repository_tree"
TOOL_LIST_TAGS = "gitlab_list_tags"
TOOL_LIST_USER_EVENTS = "gitlab_list_user_events"
TOOL_LIST_PROJECT_MEMBERS = "gitlab_list_project_members"
TOOL_LIST_PROJECT_HOOKS = "gitlab_list_project_hooks"
TOOL_LIST_RELEASES = "gitlab_list_releases"