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
ERROR_NO_TOKEN = os.getenv("GITLAB_ERROR_NO_TOKEN", """No GitLab authentication token found.

To fix:
1. Set environment variable: export GITLAB_PRIVATE_TOKEN='your-token-here'
2. Or: export GITLAB_OAUTH_TOKEN='your-oauth-token'
3. Create token at: GitLab > Settings > Access Tokens

Required scopes: api, read_api""")

ERROR_AUTH_FAILED = os.getenv("GITLAB_ERROR_AUTH_FAILED", """Authentication failed.

Possible causes:
1. Token expired - Create new token
2. Insufficient permissions - Check token scopes
3. Wrong GitLab instance - Verify GITLAB_URL

To debug:
- Test token: curl -H "PRIVATE-TOKEN: your-token" https://gitlab.com/api/v4/user
- Check scopes at: GitLab > Settings > Access Tokens""")

ERROR_NOT_FOUND = os.getenv("GITLAB_ERROR_NOT_FOUND", """The requested resource was not found.

Common causes:
1. Wrong ID/path - Double-check the identifier
2. No access - Verify project permissions
3. Resource deleted - Check if it still exists

To fix:
- For projects: Use gitlab_list_projects to find correct ID
- For issues/MRs: Verify the IID is correct (e.g., 123 not #123)""")

ERROR_RATE_LIMIT = os.getenv("GITLAB_ERROR_RATE_LIMIT", """Rate limit exceeded.

GitLab API limits:
- Authenticated: 600 requests/minute
- Unauthenticated: 60 requests/minute

To resolve:
1. Wait a few minutes before retrying
2. Reduce request frequency
3. Use pagination for large datasets
4. Check rate limit headers in response""")

ERROR_GENERIC = os.getenv("GITLAB_ERROR_GENERIC", """An unexpected error occurred.

To troubleshoot:
1. Check your internet connection
2. Verify GitLab service status: https://status.gitlab.com
3. Review the error details above
4. Try the operation again

If persists: Check logs or report issue""")

ERROR_NO_PROJECT = os.getenv("GITLAB_ERROR_NO_PROJECT", """No GitLab project detected or specified.

To fix this error:
1. Run from within a git repository with GitLab remote:
   - Check: git remote -v
   - Should show GitLab URL

2. OR provide project_id parameter:
   - As number: project_id=12345
   - As path: project_id='group/project'

3. Find your project ID:
   - Visit project on GitLab
   - Check Settings > General
   - Or use gitlab_list_projects tool

Example fix:
- cd /path/to/your/gitlab/repo
- OR add: project_id='mygroup/myproject'""")

ERROR_INVALID_INPUT = os.getenv("GITLAB_ERROR_INVALID_INPUT", """Invalid input provided.

Common issues:
1. Wrong parameter type (e.g., string instead of integer)
2. Missing required parameters
3. Invalid format (e.g., date format)

To fix:
- Check parameter descriptions
- Verify data types match requirements
- Use examples from documentation
- For IIDs: Use number only (123, not #123 or !123)""")

# Additional error messages
ERROR_INVALID_REF = os.getenv("GITLAB_ERROR_INVALID_REF", """Invalid git reference specified.

Valid references include:
- Branch names: 'main', 'develop', 'feature/xyz'
- Tags: 'v1.0.0', 'release-2024'
- Commit SHAs: 'abc1234' (min 7 chars)

To check available refs:
- Branches: Use gitlab_list_branches
- Tags: Use gitlab_list_tags
- Commits: Use gitlab_list_commits""")

ERROR_PERMISSION_DENIED = os.getenv("GITLAB_ERROR_PERMISSION_DENIED", """Permission denied for this operation.

Possible causes:
1. Insufficient access level in project
2. Protected branch restrictions
3. Approval rules not met

To resolve:
- Check your project role (need Developer/Maintainer)
- Verify branch protection settings
- Ensure MR approvals are met
- Contact project owner for access""")

ERROR_MERGE_CONFLICT = os.getenv("GITLAB_ERROR_MERGE_CONFLICT", """Cannot merge due to conflicts.

To resolve:
1. Use gitlab_rebase_merge_request to rebase
2. OR resolve conflicts locally:
   - git checkout feature-branch
   - git rebase main
   - Fix conflicts
   - git push --force-with-lease

3. Then retry the merge operation""")

ERROR_PIPELINE_REQUIRED = os.getenv("GITLAB_ERROR_PIPELINE_REQUIRED", """Pipeline must pass before merging.

Current pipeline status prevents merge.
Options:
1. Wait for pipeline to complete
2. Fix failing pipeline jobs
3. Use merge_when_pipeline_succeeds=true
4. Check project settings for pipeline requirements""")

# Tool names (for consistency)
TOOL_LIST_PROJECTS = "gitlab_list_projects"
TOOL_GET_PROJECT = "gitlab_get_project"
TOOL_LIST_ISSUES = "gitlab_list_issues"
TOOL_CREATE_ISSUE = "gitlab_create_issue"
TOOL_LIST_MRS = "gitlab_list_merge_requests"
TOOL_CREATE_MR = "gitlab_create_merge_request"
TOOL_LIST_PIPELINES = "gitlab_list_pipelines"
TOOL_LIST_BRANCHES = "gitlab_list_branches"
TOOL_GET_CURRENT_PROJECT = "gitlab_get_current_project"
TOOL_GET_MR_NOTES = "gitlab_get_merge_request_notes"

# New renamed tools
TOOL_LIST_COMMITS = "gitlab_list_commits"
TOOL_LIST_REPOSITORY_TREE = "gitlab_list_repository_tree"
TOOL_LIST_TAGS = "gitlab_list_tags"
TOOL_LIST_USER_EVENTS = "gitlab_list_user_events"
TOOL_LIST_PROJECT_MEMBERS = "gitlab_list_project_members"
TOOL_LIST_PROJECT_HOOKS = "gitlab_list_project_hooks"
TOOL_LIST_RELEASES = "gitlab_list_releases"
