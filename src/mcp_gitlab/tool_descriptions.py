"""Common descriptions and parameter definitions for GitLab tools

This module provides standardized descriptions for all GitLab MCP tool parameters and operations.
For GitLab API documentation, see: https://docs.gitlab.com/ee/api/
"""

# Import error messages from constants
from mcp_gitlab.constants import (
    ERROR_NO_PROJECT,
    ERROR_INVALID_REF,
    ERROR_PERMISSION_DENIED,
    ERROR_MERGE_CONFLICT,
    ERROR_PIPELINE_REQUIRED,
    ERROR_NO_TOKEN,
    ERROR_AUTH_FAILED,
    ERROR_NOT_FOUND,
    ERROR_RATE_LIMIT,
    ERROR_GENERIC,
    ERROR_INVALID_INPUT
)

# ============================================================================
# AUTHENTICATION & USER TOOL DESCRIPTIONS
# ============================================================================

DESC_GET_CURRENT_USER = """Get the currently authenticated user's profile
Returns comprehensive information about the authenticated user including:
- Basic info: ID, username, name, email
- Profile details: bio, organization, job title
- Account status: state, creation date, admin status
- Permissions: can_create_group, can_create_project
- Security: two_factor_enabled, external status

Use cases:
- Verify authentication is working
- Get user context for automation scripts
- Check user permissions and capabilities
- Display user info in applications

Example response: {'id': 123, 'username': 'johndoe', 'name': 'John Doe', ...}"""

DESC_GET_USER = """Get details for a specific user by ID or username
Retrieves public profile information for any GitLab user.

Parameters:
- user_id: Numeric user ID (e.g., 12345)
- username: Username string (e.g., 'johndoe')

Use either user_id OR username, not both.

Returns user information including:
- Basic info: ID, username, name
- Profile: avatar_url, web_url, bio
- Organization details: company, job title
- Account status and creation date

Use cases:
- Look up user for @mentions
- Get user info for permissions/assignments
- Find user details from commits/issues
- User profile display

Example: user_id=123 OR username='johndoe'"""

DESC_USER_ID = """User ID (numeric)
Type: integer
Format: Numeric user ID
Example: 12345
How to find: From user profile URL or API responses"""

DESC_USERNAME = """Username
Type: string
Format: GitLab username (without @)
Example: 'johndoe' (not '@johndoe')
Note: Case-sensitive, exact match required"""

# ============================================================================
# COMMON PARAMETER DESCRIPTIONS
# ============================================================================

# Pagination Parameters
DESC_PER_PAGE = """Number of results per page
Type: integer
Range: 1-100
Default: 20
Example: 50 (for faster browsing)
Tip: Use smaller values (10-20) for detailed operations, larger (50-100) for listing"""

DESC_PAGE_NUMBER = """Page number for pagination
Type: integer
Range: ≥1
Default: 1
Example: 3 (to get the third page of results)
Note: Use with per_page to navigate large result sets"""

# Project Identification
DESC_PROJECT_ID = """Project identifier (auto-detected if not provided)
Type: integer OR string
Format: numeric ID or 'namespace/project'
Optional: Yes - auto-detects from current git repository
Examples:
  - 12345 (numeric ID)
  - 'gitlab-org/gitlab' (namespace/project path)
  - 'my-group/my-subgroup/my-project' (nested groups)
Note: If in a git repo with GitLab remote, this can be omitted"""

DESC_GROUP_ID = """Group identifier
Type: integer OR string
Format: numeric ID or 'group/subgroup' path
Required: Yes
Examples:
  - 456 (numeric ID)
  - 'my-group' (group path)
  - 'parent-group/sub-group' (nested group path)"""

DESC_PROJECT_ID_REQUIRED = """Project identifier (required)
Type: integer OR string
Format: numeric ID or 'namespace/project'
Required: Yes
Examples:
  - 12345 (numeric ID from project settings)
  - 'gitlab-org/gitlab' (full path from URL)
  - 'my-company/backend/api-service' (nested groups)
How to find: Check project URL or Settings > General > Project ID"""

# Search and Filtering
DESC_SEARCH_TERM = """Search query
Type: string
Matching: Case-insensitive, partial matching
Searches in: Project names and descriptions
Examples:
  - 'frontend' (finds 'frontend-app', 'old-frontend', etc.)
  - 'API' (matches 'api', 'API', 'GraphQL-API', etc.)
Tip: Use specific terms for better results"""

# Git References
DESC_REF = """Git reference
Type: string
Format: branch name, tag name, or commit SHA
Optional: Yes - defaults to project's default branch
Examples:
  - 'main' (branch)
  - 'feature/new-login' (feature branch)
  - 'v2.0.0' (tag)
  - 'abc1234' (short commit SHA)
  - 'e83c5163316f89bfbde7d9ab23ca2e25604af290' (full SHA)
Default: Project's default branch (usually 'main' or 'master')"""

# State Filters
DESC_STATE_ISSUE = """Issue state filter
Type: string (enum)
Options: 'opened' | 'closed' | 'all'
Default: 'all'
Examples:
  - 'opened' (only open issues)
  - 'closed' (only closed issues)
  - 'all' (both open and closed)
Use case: Filter to see only active work items"""

DESC_STATE_MR = """Merge request state filter
Type: string (enum)
Options: 'opened' | 'closed' | 'merged' | 'all'
Default: 'all'
Examples:
  - 'opened' (active MRs needing review)
  - 'merged' (completed MRs)
  - 'closed' (abandoned MRs)
  - 'all' (everything)
Use case: Focus on MRs needing attention"""

# IID (Internal ID) Parameters
DESC_ISSUE_IID = """Issue number (IID - Internal ID)
Type: integer
Format: Project-specific issue number (without #)
Required: Yes
Examples:
  - 123 (for issue #123)
  - 4567 (for issue #4567)
How to find: Look at issue URL or title
  - URL: https://gitlab.com/group/project/-/issues/123 → use 123
  - Title: "Fix login bug (#123)" → use 123
Note: This is NOT the global issue ID"""

DESC_MR_IID = """Merge request number (IID - Internal ID)
Type: integer
Format: Project-specific MR number (without !)
Required: Yes
Examples:
  - 456 (for MR !456)
  - 7890 (for MR !7890)
How to find: Look at MR URL or title
  - URL: https://gitlab.com/group/project/-/merge_requests/456 → use 456
  - Title: "Add new feature (!456)" → use 456
Note: This is NOT the global MR ID"""

# File and Path Parameters
DESC_FILE_PATH = """File path in repository
Type: string
Format: Relative path from repository root using forward slashes
Required: Yes
Examples:
  - 'README.md' (root file)
  - 'src/main.py' (nested file)
  - 'docs/api/endpoints.md' (deeply nested)
  - '.github/workflows/ci.yml' (hidden directory)
Note: Always use forward slashes, even on Windows"""

DESC_TREE_PATH = """Directory path in repository
Type: string
Format: Relative path using forward slashes
Default: '' (empty string for root)
Examples:
  - '' (repository root)
  - 'src' (src directory)
  - 'src/components' (nested directory)
  - 'tests/unit/models' (deeply nested)
Note: Don't include trailing slash"""

# Commit Parameters
DESC_COMMIT_SHA = """Git commit SHA
Type: string
Format: Abbreviated (min 7 chars) or full 40-character SHA
Required: Yes
Examples:
  - 'a1b2c3d' (short form - minimum 7 characters)
  - 'a1b2c3d4e5f6' (medium form)
  - 'e83c5163316f89bfbde7d9ab23ca2e25604af290' (full SHA)
How to find: git log, GitLab UI, or MR/commit pages"""

# User Parameters
DESC_USERNAME = """GitLab username
Type: string
Format: Username without @ symbol
Case: Case-sensitive
Required: Yes
Examples:
  - 'johndoe' (for @johndoe)
  - 'mary-smith' (for @mary-smith)
  - 'user123' (for @user123)
Note: This is the username, not display name or email"""

# Boolean Filters
DESC_OWNED_PROJECTS = """Filter for owned projects only
Type: boolean
Default: false
Options:
  - true: Only projects where you are the owner
  - false: All accessible projects
Use case: Quickly find your personal projects"""

DESC_OWNED_GROUPS = """Filter for owned groups only
Type: boolean
Default: false
Options:
  - true: Only groups where you are the owner
  - false: All accessible groups
Use case: Managing your own groups"""

DESC_WITH_PROJECTS = """Include projects in group response
Type: boolean
Default: false
Options:
  - true: Include first page of projects
  - false: Only group metadata
Note: Adds project list to response (limited to first 20)"""

DESC_INCLUDE_SUBGROUPS = """Include projects from subgroups
Type: boolean
Default: false
Options:
  - true: Include all descendant group projects
  - false: Only direct group projects
Use case: Navigating hierarchical group structures"""

# Path Parameters
DESC_GIT_PATH = """Local git repository path
Type: string
Format: Absolute or relative file system path
Default: '.' (current directory)
Examples:
  - '.' (current directory)
  - '/home/user/projects/my-app' (absolute path)
  - '../other-project' (relative path)
  - '~/repos/gitlab-project' (home directory)
Use case: Detect project from a different directory"""

# Sorting Parameters
DESC_SORT_ORDER = """Sort direction
Type: string (enum)
Options: 'asc' | 'desc'
Default: Varies by context (usually 'desc' for time-based)
Examples:
  - 'asc': A→Z, oldest→newest, smallest→largest
  - 'desc': Z→A, newest→oldest, largest→smallest"""

DESC_ORDER_BY = """Field to sort by
Type: string (enum)
Options vary by endpoint:
  - Commits: 'created_at', 'title'
  - Issues: 'created_at', 'updated_at', 'priority', 'due_date'
  - MRs: 'created_at', 'updated_at', 'title'
Default: Usually 'created_at'
Example: 'updated_at' to see recently modified items first"""

# Content Parameters
DESC_MAX_BODY_LENGTH = """Maximum length for text content
Type: integer
Range: 0-10000 (0 = unlimited)
Default: 1000
Examples:
  - 0: Show full content (no truncation)
  - 500: Limit to 500 characters
  - 2000: Allow longer descriptions
Note: Truncated text ends with '...'"""

DESC_RECURSIVE = """Include subdirectories
Type: boolean
Default: false
Options:
  - true: Include all subdirectories recursively
  - false: Only immediate children
Use case: true for full directory tree, false for folder contents"""

# Date Parameters
DESC_DATE_SINCE = """Start date for filtering
Type: string
Format: ISO 8601 (YYYY-MM-DD or full timestamp)
Optional: Yes
Examples:
  - '2024-01-01' (from start of year)
  - '2024-01-01T00:00:00Z' (with time, UTC)
  - '2024-01-01T09:00:00+02:00' (with timezone)
Timezone: Defaults to UTC if not specified
Use case: Filter commits/events after a specific date"""

DESC_DATE_UNTIL = """End date for filtering
Type: string
Format: ISO 8601 (YYYY-MM-DD or full timestamp)
Optional: Yes
Examples:
  - '2024-12-31' (until end of year)
  - '2024-12-31T23:59:59Z' (end of day, UTC)
  - '2024-12-31T17:00:00-05:00' (with timezone)
Timezone: Defaults to UTC if not specified
Use case: Filter commits/events before a specific date"""

# Filter Parameters
DESC_PATH_FILTER = """File path filter for commits
Type: string
Format: Relative file path
Optional: Yes
Examples:
  - 'src/main.py' (commits touching this file)
  - 'docs/' (commits in docs directory)
  - 'package.json' (dependency updates)
Use case: Track history of specific files"""

DESC_INCLUDE_STATS = """Include statistics
Type: boolean
Default: false
Options:
  - true: Include additions, deletions, total changes
  - false: Basic information only
Use case: true for code review, false for quick browsing"""

DESC_SEARCH_SCOPE = """Search scope
Type: string (enum)
Options:
  - 'issues': Search in issues
  - 'merge_requests': Search in MRs
  - 'milestones': Search in milestones
  - 'wiki_blobs': Search in wiki pages
  - 'commits': Search in commit messages
  - 'blobs': Search in file contents
  - 'users': Search for users
Required: Yes
Example: 'issues' to find issues mentioning a term"""

# Branch and Tag Parameters
DESC_BRANCH_TAG_REF = """Branch or tag name
Type: string
Format: Valid git reference name
Optional: Yes
Examples:
  - 'main' (main branch)
  - 'develop' (development branch)
  - 'feature/user-auth' (feature branch)
  - 'v1.0.0' (version tag)
  - 'release-2024.01' (release tag)"""

# Event Filters
DESC_ACTION_FILTER = """Event action filter
Type: string (enum)
Options:
  - 'created': New items created
  - 'updated': Existing items modified
  - 'closed': Items closed
  - 'reopened': Items reopened
  - 'pushed': Code pushed
  - 'commented': Comments added
  - 'merged': MRs merged
  - 'joined': User joined project
  - 'left': User left project
  - 'destroyed': Items deleted
  - 'expired': Items expired
Optional: Yes (returns all actions if not specified)"""

DESC_TARGET_TYPE_FILTER = """Event target type filter
Type: string (enum)
Options:
  - 'Issue': Issue events
  - 'MergeRequest': MR events
  - 'Milestone': Milestone events
  - 'Note': Comment events
  - 'Project': Project events
  - 'Snippet': Snippet events
  - 'User': User events
Optional: Yes (returns all types if not specified)"""

DESC_DATE_AFTER = """Start date for event filtering
Type: string
Format: ISO 8601 date
Inclusive: Yes
Optional: Yes
Examples:
  - '2024-01-01' (events from start of 2024)
  - '2024-06-15T14:00:00Z' (specific time)
See also: DESC_DATE_SINCE for similar functionality"""

DESC_DATE_BEFORE = """End date for event filtering
Type: string
Format: ISO 8601 date
Inclusive: Yes
Optional: Yes
Examples:
  - '2024-12-31' (events until end of 2024)
  - '2024-06-15T14:00:00Z' (specific time)
See also: DESC_DATE_UNTIL for similar functionality"""

# ============================================================================
# COMPLEX PARAMETER DESCRIPTIONS
# ============================================================================

# Content Parameters
DESC_TITLE = """Title text
Type: string
Required: Yes (for create/update operations)
Max length: 255 characters
Format: Plain text with emoji support
Examples:
  - 'Fix login validation bug'
  - '🚀 Add new feature: Dark mode'
  - 'Update dependencies to latest versions'
Note: Supports Unicode and special characters"""

DESC_DESCRIPTION = """Description content
Type: string
Format: GitLab Flavored Markdown (GFM)
Optional: Yes
Features supported:
  - Mentions: @username
  - Issue references: #123
  - MR references: !456
  - Task lists: - [ ] Task
  - Code blocks with syntax highlighting
  - Tables, links, images
Examples:
  'Fixes #123 by updating validation logic.
  
  - [x] Add input validation
  - [ ] Update tests
  
  cc @teamlead for review'"""

# Assignment Parameters
DESC_ASSIGNEE_ID = """Single assignee user ID
Type: integer
Format: GitLab user ID (not username)
Optional: Yes
Examples:
  - 12345 (user's numeric ID)
  - null (to unassign)
How to find: User profile URL or API
Note: For multiple assignees, use assignee_ids instead"""

DESC_ASSIGNEE_IDS = """Multiple assignee user IDs
Type: array of integers
Format: List of GitLab user IDs
Optional: Yes
Examples:
  - [123, 456, 789] (assign to 3 users)
  - [123] (assign to 1 user)
  - [] (unassign all)
Note: Premium feature for multiple assignees"""

DESC_REVIEWER_IDS = """Reviewer user IDs
Type: array of integers
Format: List of GitLab user IDs
Optional: Yes
Examples:
  - [234, 567] (request review from 2 users)
  - [234] (single reviewer)
  - [] (remove all reviewers)
Use case: Request code review from specific team members"""

# Labels and Milestones
DESC_LABELS = """Labels to apply
Type: string
Format: Comma-separated label names
Optional: Yes
Examples:
  - 'bug' (single label)
  - 'bug,priority::high' (multiple labels)
  - 'backend,needs-review,v2.0' (many labels)
  - '' (empty string to remove all labels)
Note: Creates new labels if they don't exist"""

DESC_MILESTONE_ID = """Milestone ID
Type: integer or null
Format: Milestone's numeric ID
Optional: Yes
Examples:
  - 42 (assign to milestone with ID 42)
  - null (remove from milestone)
How to find: Milestone page or API
Note: Milestone must exist in the project"""

# State Management
DESC_STATE_EVENT = """State transition
Type: string (enum)
Options:
  - 'close': Close the issue/MR
  - 'reopen': Reopen a closed issue/MR
Optional: Yes
Examples:
  - 'close' (mark as closed)
  - 'reopen' (reactivate)
Use case: Change issue/MR state without other updates"""

# Merge Request Options
DESC_REMOVE_SOURCE_BRANCH = """Delete source branch after merge
Type: boolean
Default: false
Options:
  - true: Delete branch after successful merge
  - false: Keep branch after merge
Requirements: User must have permission to delete
Use case: Automatic cleanup of feature branches"""

DESC_SQUASH = """Squash commits on merge
Type: boolean
Default: Follows project settings
Options:
  - true: Combine all commits into one
  - false: Keep all commits
  - null: Use project default
Use case: Clean commit history"""

DESC_DISCUSSION_LOCKED = """Lock discussions
Type: boolean
Default: false
Options:
  - true: Only project members can comment
  - false: Anyone can comment
Use case: Prevent spam or off-topic comments"""

DESC_ALLOW_COLLABORATION = """Allow commits from members
Type: boolean
Default: true
Options:
  - true: Upstream members can push to fork branch
  - false: Only fork owner can push
Use case: Let maintainers fix small issues directly"""

DESC_TARGET_BRANCH = """Target branch for merge
Type: string
Required: Yes
Format: Existing branch name
Examples:
  - 'main' (merge into main)
  - 'develop' (merge into develop)
  - 'release/v2.0' (merge into release branch)
Note: Branch must exist in the project"""

DESC_MERGE_WHEN_PIPELINE_SUCCEEDS = """Auto-merge on pipeline success
Type: boolean
Default: false
Options:
  - true: Merge automatically when CI passes
  - false: Manual merge required
Requirements: Pipeline must be running
Use case: Ensure CI passes before merging"""

DESC_MERGE_COMMIT_MESSAGE = """Custom merge commit message
Type: string
Optional: Yes
Variables supported:
  - %{title}: MR title
  - %{description}: MR description
  - %{reference}: MR reference (!123)
Example: 'Merge %{title} (%{reference})'
Default: GitLab's default format"""

DESC_SQUASH_COMMIT_MESSAGE = """Custom squash commit message
Type: string
Optional: Yes
Variables supported: Same as merge_commit_message
Example: '%{title} (#%{reference})'
Use case: Customize squashed commit message"""

# Comments and Discussions
DESC_COMMENT_BODY = """Comment content
Type: string
Required: Yes
Format: GitLab Flavored Markdown
Features:
  - Mentions: @username
  - References: #123, !456
  - Code blocks: ```language
  - Task lists: - [ ] Task
  - Slash commands: /assign @user
Examples:
  'LGTM! 👍'
  
  'Found an issue in line 42:
  ```python
  # This could be None
  result = data["key"]
  ```
  Should check if key exists first.'"""

# Diff and Comparison Parameters
DESC_FROM_REF = """Source reference for comparison
Type: string
Required: Yes
Format: Branch, tag, or commit SHA
Examples:
  - 'feature/new-api' (branch)
  - 'v1.0.0' (tag)
  - 'abc123def' (commit)
Use case: Starting point for comparison"""

DESC_TO_REF = """Target reference for comparison
Type: string
Required: Yes
Format: Branch, tag, or commit SHA
Examples:
  - 'main' (branch)
  - 'v2.0.0' (tag)
  - '456789abc' (commit)
Use case: Ending point for comparison"""

DESC_STRAIGHT = """Diff type
Type: boolean
Default: false
Options:
  - true: Direct comparison (A..B)
  - false: Three-dot comparison (A...B)
Explanation:
  - Direct: All changes between two points
  - Three-dot: Changes in B since common ancestor
Use case: false for MR-style diffs, true for direct comparison"""

# Tag and Release Parameters
DESC_ORDER_BY_TAG = """Tag ordering field
Type: string (enum)
Options:
  - 'name': Alphabetical order
  - 'updated': Last updated first
  - 'version': Version string comparison
  - 'semver': Semantic version sorting
Default: 'updated'
Examples:
  - 'name': a-tag, b-tag, c-tag
  - 'semver': v1.0.0, v1.1.0, v2.0.0"""

# Commit Parameters
DESC_BRANCH = """Target branch for commits
Type: string
Required: Yes
Format: Existing branch name
Examples:
  - 'main' (commit to main)
  - 'feature/add-login' (feature branch)
  - 'hotfix/security-patch' (hotfix branch)
Note: Branch must exist before committing"""

DESC_COMMIT_MESSAGE = """Commit message
Type: string
Required: Yes
Format: Conventional commits recommended
Structure:
  - First line: Summary (50-72 chars)
  - Blank line
  - Body: Detailed description
  - Footer: References, breaking changes
Examples:
  'feat: Add user authentication

  Implement JWT-based authentication with refresh tokens.
  Store tokens securely in httpOnly cookies.

  Closes #123'"""

DESC_ACTIONS = """File operations for commit
Type: array of objects
Required: Yes
Max items: 100 per commit
Structure:
{
  "action": "create" | "update" | "delete" | "move",
  "file_path": "string (required)",
  "content": "string (required for create/update)",
  "encoding": "text" | "base64" (optional, default: text)",
  "previous_path": "string (required for move)"
}

Examples:
[
  {
    "action": "create",
    "file_path": "src/config.json",
    "content": "{\"debug\": true}"
  },
  {
    "action": "update",
    "file_path": "README.md",
    "content": "# Updated README\\n\\nNew content here"
  },
  {
    "action": "delete",
    "file_path": "old-file.txt"
  },
  {
    "action": "move",
    "file_path": "new-location/file.txt",
    "previous_path": "old-location/file.txt"
  }
]

Use cases:
- create: Add new files
- update: Modify existing files
- delete: Remove files
- move: Rename or relocate files"""

DESC_AUTHOR_EMAIL = """Commit author email
Type: string
Format: Valid email address
Optional: Yes (uses authenticated user's email)
Examples:
  - 'john.doe@example.com'
  - 'bot@automated-system.com'
Use case: Override for automated commits"""

DESC_AUTHOR_NAME = """Commit author name
Type: string
Format: Any string
Optional: Yes (uses authenticated user's name)
Examples:
  - 'John Doe'
  - 'Automated Bot'
  - 'CI System'
Use case: Override for automated commits"""

# Search Parameters
DESC_QUERY = """Search query
Type: string
Format: Free text search
Searches in: Usernames, names, emails
Matching: Partial, case-insensitive
Examples:
  - 'john' (finds 'john', 'johnny', 'Johnson')
  - 'admin' (finds users with admin in name)
  - 'example.com' (finds users with that email domain)"""

# Discussion Parameters
DESC_DISCUSSION_ID = """Discussion thread ID
Type: string
Required: Yes
Format: SHA-like identifier
How to get: From gitlab_get_merge_request_discussions
Example: '6a9c1750b37d513a43987b574953fceb50b03ce7'
Use case: Resolve specific discussion thread"""

# Pipeline Parameters
DESC_PIPELINE_ID = """Pipeline ID
Type: integer
Required: Yes
Format: Numeric pipeline identifier
How to get: From gitlab_list_pipelines or MR details
Example: 123456
Use case: Get details of specific CI/CD run"""

# Summary Parameters
DESC_MAX_LENGTH = """Maximum summary length
Type: integer
Range: 100-5000
Default: 500
Examples:
  - 300: Very concise summary
  - 500: Standard summary
  - 1000: Detailed summary
Use case: Control output size for LLM context"""

# Diff Parameters
DESC_CONTEXT_LINES = """Context lines in diff
Type: integer
Range: 0-10
Default: 3
Examples:
  - 0: Only changed lines
  - 3: Standard context
  - 10: Maximum context
Use case: Balance between context and size"""

DESC_MAX_FILE_SIZE = """Maximum file size for diffs
Type: integer
Unit: Bytes
Default: 50000 (50KB)
Examples:
  - 10000: 10KB limit
  - 50000: 50KB (default)
  - 100000: 100KB for larger files
Use case: Prevent huge diffs from overwhelming output"""

# Batch Operations
DESC_OPERATIONS = """Batch operations list
Type: array of objects
Required: Yes
Structure:
{
  "name": "string (operation identifier)",
  "tool": "string (GitLab tool name)",
  "arguments": "object (tool-specific arguments)"
}

Features:
- Sequential execution
- Result referencing: {{operation_name.field}}
- Automatic rollback on failure

Examples:
[
  {
    "name": "create_branch",
    "tool": "gitlab_create_branch",
    "arguments": {
      "branch": "feature/new-feature",
      "ref": "main"
    }
  },
  {
    "name": "create_file",
    "tool": "gitlab_create_commit",
    "arguments": {
      "branch": "{{create_branch.name}}",
      "commit_message": "Add new feature",
      "actions": [{
        "action": "create",
        "file_path": "feature.py",
        "content": "# New feature"
      }]
    }
  },
  {
    "name": "create_mr",
    "tool": "gitlab_create_merge_request",
    "arguments": {
      "source_branch": "{{create_branch.name}}",
      "target_branch": "main",
      "title": "Add new feature"
    }
  }
]

Use cases:
- Complex workflows
- Dependent operations
- Atomic multi-step changes"""

DESC_STOP_ON_ERROR = """Error handling strategy
Type: boolean
Default: true
Options:
  - true: Stop and rollback on first error
  - false: Continue, collect all errors
Use cases:
  - true: Critical operations requiring all-or-nothing
  - false: Best-effort batch processing"""

# ============================================================================
# TOOL DESCRIPTIONS
# ============================================================================

# Project Management Tools
DESC_LIST_PROJECTS = """List accessible GitLab projects
Returns: Array of project summaries with ID, name, description, URL
Use when: Browsing projects, finding project IDs
Pagination: Yes (default 20 per page)
Filtering: By ownership, name search

Example response:
[{
  "id": 12345,
  "name": "my-project",
  "path_with_namespace": "group/my-project",
  "description": "Project description",
  "web_url": "https://gitlab.com/group/my-project"
}]

Related tools:
- gitlab_get_project: Get full project details
- gitlab_search_projects: Search all GitLab projects"""

DESC_GET_PROJECT = """Get detailed project information
Returns: Complete project metadata, settings, statistics
Use when: Need full project details, checking configuration
Required: Project ID or path

Example response:
{
  "id": 12345,
  "name": "my-project",
  "path_with_namespace": "group/my-project",
  "default_branch": "main",
  "visibility": "private",
  "issues_enabled": true,
  "merge_requests_enabled": true,
  "wiki_enabled": true,
  "statistics": {
    "commit_count": 1024,
    "repository_size": 15728640
  }
}

Related tools:
- gitlab_list_projects: Find projects
- gitlab_get_current_project: Auto-detect from git"""


DESC_GET_CURRENT_PROJECT = """Auto-detect project from git repository
Returns: Same as gitlab_get_project
Use when: Working in a git repo with GitLab remote
No parameters needed: Examines git remotes

How it works:
1. Checks git remotes in current/specified directory
2. Identifies GitLab URLs
3. Fetches project details from API

Related tools:
- gitlab_get_project: When you know the project ID
- gitlab_list_projects: Browse available projects"""

# Group Management Tools
DESC_LIST_GROUPS = """List accessible GitLab groups
Returns: Array of groups with ID, name, path, description
Use when: Browsing groups, finding group IDs, navigating group hierarchy
Pagination: Yes (default 50 per page)
Filtering: By ownership, name search

Example response:
[{
  "id": 123,
  "name": "My Group",
  "path": "my-group",
  "full_path": "parent-group/my-group",
  "description": "Group for team projects",
  "web_url": "https://gitlab.com/groups/my-group",
  "visibility": "private"
}]

Related tools:
- gitlab_get_group: Get full group details
- gitlab_list_group_projects: List projects in a group"""

DESC_GET_GROUP = """Get detailed group information
Returns: Complete group metadata, settings, statistics
Use when: Need full group details, checking configuration, counting projects
Optional: Include first page of projects with with_projects=true

Example response:
{
  "id": 123,
  "name": "My Group",
  "full_path": "parent-group/my-group",
  "description": "Group for team projects",
  "visibility": "private",
  "projects_count": 15,
  "created_at": "2023-01-01T00:00:00Z",
  "web_url": "https://gitlab.com/groups/my-group"
}

Related tools:
- gitlab_list_groups: Browse available groups
- gitlab_list_group_projects: List all projects in group"""

DESC_LIST_GROUP_PROJECTS = """List projects within a group
Returns: Array of projects belonging to the specified group
Use when: Browsing group projects, finding projects in group hierarchy
Pagination: Yes (default 50 per page)
Options: Include subgroup projects with include_subgroups=true

Example response:
[{
  "id": 456,
  "name": "project-one",
  "path_with_namespace": "my-group/project-one",
  "description": "First project in group",
  "web_url": "https://gitlab.com/my-group/project-one"
}]

Related tools:
- gitlab_get_group: Get group details
- gitlab_get_project: Get full project details"""

# Issue Management Tools
DESC_LIST_ISSUES = """List project issues
Returns: Array of issues with details
Use when: Browsing issues, finding work items
Filtering: By state (opened/closed/all)
Pagination: Yes (default 20 per page)

Example response:
[{
  "iid": 123,
  "title": "Fix login bug",
  "state": "opened",
  "labels": ["bug", "high-priority"],
  "assignees": [{"username": "johndoe"}],
  "web_url": "https://gitlab.com/group/project/-/issues/123"
}]

Related tools:
- gitlab_get_issue: Get full issue details
- gitlab_add_issue_comment: Comment on issue
- gitlab_search_in_project: Search issue content"""

DESC_GET_ISSUE = """Get complete issue details
Returns: Full issue data including description, comments count
Use when: Need complete issue information
Required: Issue IID (e.g., 123 for issue #123)

What's IID?: Internal ID - the issue number shown in GitLab
Example: For issue #123, use iid=123

Returns:
{
  "iid": 123,
  "title": "Fix login bug",
  "description": "Detailed bug description...",
  "state": "opened",
  "labels": ["bug"],
  "milestone": {"title": "v2.0"},
  "time_stats": {
    "time_estimate": 7200,
    "total_time_spent": 3600
  }
}

Related tools:
- gitlab_list_issues: Find issues
- gitlab_add_issue_comment: Add comment
- gitlab_update_issue: Modify issue"""

# Merge Request Tools
DESC_LIST_MRS = """List project merge requests
Returns: Array of MRs with key information
Use when: Reviewing MRs, finding specific MRs
Filtering: By state (opened/closed/merged/all)
Pagination: Yes (default 20 per page)

Example response:
[{
  "iid": 456,
  "title": "Add new feature",
  "state": "opened",
  "source_branch": "feature/new-feature",
  "target_branch": "main",
  "draft": false,
  "has_conflicts": false,
  "web_url": "https://gitlab.com/group/project/-/merge_requests/456"
}]

Related tools:
- gitlab_get_merge_request: Full MR details
- gitlab_get_merge_request_changes: View diffs
- gitlab_merge_merge_request: Merge an MR"""

DESC_GET_MR = """Get complete merge request details
Returns: Full MR data with pipelines, approvals, conflicts
Use when: Reviewing MR, checking merge status
Required: MR IID (e.g., 456 for MR !456)

What's IID?: Internal ID - the MR number shown in GitLab
Example: For MR !456, use iid=456

Returns:
{
  "iid": 456,
  "title": "Add new feature",
  "state": "opened",
  "merge_status": "can_be_merged",
  "pipeline": {"status": "success"},
  "approvals_required": 2,
  "approvals_left": 1,
  "changes_count": "15",
  "has_conflicts": false,
  "diff_stats": {
    "additions": 150,
    "deletions": 30
  }
}

Related tools:
- gitlab_get_merge_request_changes: See actual diffs
- gitlab_get_merge_request_discussions: Read reviews
- gitlab_approve_merge_request: Approve MR
- gitlab_merge_merge_request: Merge MR"""

DESC_GET_MR_NOTES = """List merge request comments
Returns: Array of notes/comments with content
Use when: Reading MR discussions, reviews
Pagination: Yes (default 10 per page)
Sorting: By created_at or updated_at

Example response:
[{
  "id": 789,
  "body": "Great work! Just one suggestion...",
  "author": {"username": "reviewer"},
  "created_at": "2024-01-15T10:30:00Z",
  "type": "DiffNote",
  "resolvable": true,
  "resolved": false
}]

Related tools:
- gitlab_get_merge_request_discussions: Threaded discussions
- gitlab_add_merge_request_comment: Add comment
- gitlab_resolve_discussion: Resolve threads"""

# Repository File Tools
DESC_GET_FILE_CONTENT = """Get file content from repository
Returns: Raw file content as string
Use when: Reading source code, configs, documentation
Optional: Specify branch/tag/commit (defaults to default branch)

Example:
- File: 'src/main.py' → Returns Python code
- File: 'package.json' → Returns JSON content
- File: 'README.md' → Returns Markdown

Related tools:
- gitlab_list_repository_tree: Browse files
- gitlab_create_commit: Modify files
- gitlab_get_commit_diff: See file changes"""


DESC_LIST_TREE = """Browse repository directory structure
Returns: Array of files and directories
Use when: Exploring repo structure, listing files
Optional: Recursive listing, specific path

Example response:
[{
  "name": "src",
  "type": "tree",
  "path": "src",
  "mode": "040000"
}, {
  "name": "README.md",
  "type": "blob",
  "path": "README.md",
  "mode": "100644"
}]

Related tools:
- gitlab_get_file_content: Read file contents
- gitlab_search_in_project: Search in files"""

# Commit Tools

DESC_LIST_COMMITS = """List repository commits
Returns: Array of commits with details
Use when: Viewing history, finding specific changes
Filtering: By date range, file path, branch
Pagination: Yes (default 20 per page)

Example response:
[{
  "id": "e83c5163316f89bfbde7d9ab23ca2e25604af290",
  "short_id": "e83c516",
  "title": "Fix critical bug",
  "author_name": "John Doe",
  "committed_date": "2024-01-15T14:30:00Z",
  "message": "Fix critical bug\\n\\nDetailed explanation..."
}]

Related tools:
- gitlab_get_commit: Full commit details
- gitlab_get_commit_diff: See changes
- gitlab_search_in_project: Search commits"""

DESC_GET_COMMIT = """Get single commit details
Returns: Complete commit information with stats
Use when: Examining specific commit
Required: Commit SHA (short or full)

Example response:
{
  "id": "e83c5163316f89bfbde7d9ab23ca2e25604af290",
  "title": "Fix critical bug",
  "message": "Fix critical bug\\n\\nDetailed explanation...",
  "author": {"name": "John Doe", "email": "john@example.com"},
  "parent_ids": ["ae1d9fb46aa2b07ee9836d49862ec4e2c46fbbba"],
  "stats": {
    "additions": 15,
    "deletions": 3,
    "total": 18
  }
}

Related tools:
- gitlab_get_commit_diff: View changes
- gitlab_cherry_pick_commit: Apply to another branch
- gitlab_list_commits: Browse history"""

DESC_GET_COMMIT_DIFF = """Get commit diff/changes
Returns: Detailed diff of all changed files
Use when: Code review, understanding changes
Shows: Added/removed lines, file modifications

Example response:
[{
  "old_path": "src/main.py",
  "new_path": "src/main.py",
  "diff": "@@ -10,3 +10,5 @@\\n def main():\\n-    print('Hello')\\n+    print('Hello, World!')\\n+    return 0",
  "new_file": false,
  "deleted_file": false
}]

Related tools:
- gitlab_get_commit: Commit metadata
- gitlab_compare_refs: Compare branches
- gitlab_smart_diff: Advanced diff options"""

# Search Tools
DESC_SEARCH_PROJECTS = """Search all GitLab projects
Returns: Projects matching search query
Use when: Finding projects across GitLab
Scope: All public projects + your private projects

Different from list_projects:
- Searches ALL of GitLab
- list_projects only shows YOUR accessible projects

Related tools:
- gitlab_list_projects: Your projects only
- gitlab_search_in_project: Search within project"""

DESC_SEARCH_IN_PROJECT = """Search within a project
Returns: Results from specified scope
Use when: Finding issues, MRs, code, wiki pages
Required: Scope (what to search in)

Scopes:
- 'issues': Search issue titles/descriptions
- 'merge_requests': Search MR titles/descriptions
- 'commits': Search commit messages
- 'blobs': Search file contents
- 'wiki_blobs': Search wiki pages

Example: Search for "login" in issues
Returns matching issues with highlights

Related tools:
- gitlab_search_projects: Search across projects
- Specific list tools for each type"""

# Repository Info Tools
DESC_LIST_BRANCHES = """List repository branches
Returns: All branches with latest commit info
Use when: Checking branches, finding feature branches
Optional: Search filter

Example response:
[{
  "name": "main",
  "protected": true,
  "merged": false,
  "can_push": true,
  "default": true,
  "commit": {
    "id": "abc123...",
    "short_id": "abc123",
    "title": "Latest commit"
  }
}]

Related tools:
- gitlab_create_branch: Create new branch
- gitlab_delete_branch: Remove branch
- gitlab_compare_refs: Compare branches"""

DESC_LIST_PIPELINES = """List CI/CD pipelines
Returns: Pipeline runs with status
Use when: Checking CI status, finding failures
Filtering: By ref (branch), status

Statuses:
- running: Currently executing
- pending: Waiting to start
- success: Passed
- failed: Failed
- canceled: Manually canceled
- skipped: Skipped

Example response:
[{
  "id": 123456,
  "status": "success",
  "ref": "main",
  "sha": "abc123...",
  "created_at": "2024-01-15T10:00:00Z",
  "duration": 300
}]

Related tools:
- gitlab_get_pipeline: Full pipeline details
- gitlab_summarize_pipeline: AI-friendly summary"""


DESC_LIST_USER_EVENTS = """Get user's activity feed
Returns: Array of user activities
Use when: Tracking user contributions, audit trail
Filtering: By action type, target type, date range

Example activities:
- Created issue #123
- Commented on MR !456
- Pushed to branch main
- Closed issue #789

Related tools:
- gitlab_list_project_members: Find users
- gitlab_search_in_project: Search by user"""

# MR Lifecycle Tools
DESC_UPDATE_MR = """Update merge request fields
Returns: Updated MR object
Use when: Modifying MR properties
Can update: Title, description, assignees, labels, etc.

Examples:
- Change title: {"title": "New title"}
- Add reviewers: {"reviewer_ids": [123, 456]}
- Close MR: {"state_event": "close"}

Related tools:
- gitlab_get_merge_request: Check current state
- gitlab_close_merge_request: Just close
- gitlab_merge_merge_request: Merge MR"""

DESC_CLOSE_MR = """Close merge request without merging
Returns: Updated MR with closed state
Use when: Abandoning changes, deferring work
Note: Can be reopened later

Related tools:
- gitlab_update_merge_request: Reopen or other updates
- gitlab_merge_merge_request: Merge instead"""

DESC_MERGE_MR = """Merge an approved merge request
Returns: Merge result with commit SHA
Use when: MR is approved and ready
Options: Squash, delete branch, auto-merge

Prerequisites:
- No conflicts
- Approvals met
- CI passing (if required)

Related tools:
- gitlab_get_merge_request: Check merge status
- gitlab_approve_merge_request: Add approval
- gitlab_rebase_merge_request: Fix conflicts"""

# Comment Tools
DESC_ADD_ISSUE_COMMENT = """Add comment to issue
Returns: Created comment object
Use when: Providing feedback, updates
Supports: Markdown, mentions, references

Example:
"Fixed in PR !456. Please test and confirm."

Related tools:
- gitlab_get_issue: Read issue first
- gitlab_list_issues: Find issues"""

DESC_ADD_MR_COMMENT = """Add comment to merge request
Returns: Created comment object
Use when: Code review feedback, discussions
Supports: Markdown, mentions, slash commands

Example:
"LGTM! 👍 Just one minor suggestion..."

Related tools:
- gitlab_get_merge_request_notes: Read existing
- gitlab_get_merge_request_discussions: Threaded view"""

# Approval Tools
DESC_APPROVE_MR = """Approve a merge request
Returns: Approval status
Use when: Code review complete, changes approved
Note: Cannot approve your own MRs

Related tools:
- gitlab_get_merge_request_approvals: Check status
- gitlab_merge_merge_request: Merge after approval"""

DESC_GET_MR_APPROVALS = """Check MR approval status
Returns: Approval requirements and current state
Use when: Checking if MR can be merged
Shows: Required approvals, who approved

Example response:
{
  "approvals_required": 2,
  "approvals_left": 1,
  "approved_by": [
    {"user": {"username": "johndoe"}}
  ],
  "approval_rules": [...]
}

Related tools:
- gitlab_approve_merge_request: Add approval
- gitlab_merge_merge_request: Merge when ready"""

# Repository Operation Tools

DESC_LIST_TAGS = """List repository tags
Returns: Tags with commit info
Use when: Finding releases, version tags
Sorting: By name, date, semver

Example response:
[{
  "name": "v2.0.0",
  "message": "Version 2.0.0 release",
  "commit": {
    "id": "abc123...",
    "short_id": "abc123",
    "title": "Prepare 2.0.0 release"
  },
  "release": {
    "tag_name": "v2.0.0",
    "description": "Major release with new features..."
  }
}]

Related tools:
- gitlab_list_releases: Full release info
- gitlab_create_tag: Create new tag"""

DESC_CREATE_COMMIT = """Create commit with file changes
Returns: New commit details
Use when: Making changes via API
Supports: Multiple file operations in one commit

Key features:
- Atomic: All changes or none
- Multiple files: Up to 100 operations
- All operations: create, update, delete, move

Example: Add feature with test
{
  "branch": "feature/new-feature",
  "commit_message": "Add new feature with tests",
  "actions": [
    {"action": "create", "file_path": "src/feature.py", "content": "..."},
    {"action": "create", "file_path": "tests/test_feature.py", "content": "..."}
  ]
}

Related tools:
- gitlab_safe_preview_commit: Preview first
- gitlab_list_repository_tree: Check existing files"""

DESC_COMPARE_REFS = """Compare two git references
Returns: Commits and diffs between refs
Use when: Reviewing changes before merge
Shows: What changed between two points

Example: Compare feature branch to main
- from: "main"
- to: "feature/new-feature"
Shows all changes in feature branch

Related tools:
- gitlab_create_merge_request: Create MR from comparison
- gitlab_smart_diff: Advanced diff options"""

# Release and Member Tools
DESC_LIST_RELEASES = """List project releases
Returns: GitLab releases (not just tags)
Use when: Finding versions, release notes
Includes: Assets, release notes, links

Different from tags:
- Releases have descriptions, assets
- Tags are just git references

Related tools:
- gitlab_list_tags: Simple tag list
- gitlab_create_release: Create release"""


DESC_LIST_PROJECT_MEMBERS = """List project members
Returns: Users with access levels
Use when: Finding team members, permissions
Shows: Direct and inherited members

Access levels:
- 10: Guest
- 20: Reporter
- 30: Developer
- 40: Maintainer
- 50: Owner

Related tools:
- gitlab_add_project_member: Add member
- gitlab_update_member_role: Change access"""


DESC_LIST_PROJECT_HOOKS = """List project webhooks
Returns: Configured webhooks
Use when: Checking integrations
Shows: URLs, events, configuration

Example response:
[{
  "id": 1,
  "url": "https://example.com/hook",
  "push_events": true,
  "issues_events": true,
  "merge_requests_events": true,
  "wiki_page_events": false
}]

Related tools:
- gitlab_create_project_hook: Add webhook
- gitlab_test_project_hook: Test webhook"""

# MR Advanced Tools
DESC_GET_MR_DISCUSSIONS = """Get MR discussion threads
Returns: Threaded discussions with replies
Use when: Reading code review comments
Better than notes: Shows thread structure

Example response:
[{
  "id": "abc123...",
  "notes": [{
    "body": "Should we use a different approach here?",
    "author": {"username": "reviewer"},
    "resolvable": true,
    "resolved": false
  }, {
    "body": "Good point, let me refactor this.",
    "author": {"username": "author"}
  }]
}]

Related tools:
- gitlab_resolve_discussion: Mark resolved
- gitlab_add_merge_request_comment: Reply"""

DESC_RESOLVE_DISCUSSION = """Resolve a discussion thread
Returns: Updated discussion
Use when: Code review feedback addressed
Required: Discussion ID from get_discussions

Related tools:
- gitlab_get_merge_request_discussions: Find discussions
- gitlab_add_merge_request_comment: Add resolution comment"""

DESC_GET_MR_CHANGES = """Get detailed MR file changes
Returns: Complete diffs for all files
Use when: Reviewing code changes
Shows: Full file diffs with context

Similar to commit diff but for entire MR
Includes all commits in the MR

Related tools:
- gitlab_get_merge_request: MR overview
- gitlab_smart_diff: Customizable diffs"""

# MR Operation Tools
DESC_REBASE_MR = """Rebase MR onto target branch
Returns: Rebase status
Use when: MR is behind target branch
Fixes: Out-of-date MR status

Requirements:
- Fast-forward merge method
- No conflicts
- Developer access

Related tools:
- gitlab_get_merge_request: Check if rebase needed
- gitlab_merge_merge_request: Merge after rebase"""

DESC_CHERRY_PICK = """Apply commit to another branch
Returns: New commit on target branch
Use when: Backporting fixes, selective changes
Creates: New commit with same changes

Example: Backport bug fix to stable
- commit: "abc123" (fix from main)
- branch: "stable-1.0" (apply here)

Related tools:
- gitlab_get_commit: Find commit to pick
- gitlab_create_merge_request: MR for picked commit"""

# AI Helper Tools
DESC_SUMMARIZE_MR = """Generate AI-friendly MR summary
Returns: Concise summary for LLM context
Use when: Reviewing MRs with AI assistance
Includes: Key changes, discussions, status

Optimized for:
- Limited context windows
- Quick understanding
- Decision making

Related tools:
- gitlab_get_merge_request: Full details
- gitlab_summarize_issue: Issue summaries"""

DESC_SUMMARIZE_ISSUE = """Generate AI-friendly issue summary
Returns: Condensed issue information
Use when: Processing issues with AI
Includes: Title, description, comments, status

Smart truncation:
- Preserves key information
- Removes redundancy
- Fits context limits

Related tools:
- gitlab_get_issue: Full details
- gitlab_summarize_pipeline: Pipeline summaries"""

DESC_SUMMARIZE_PIPELINE = """Summarize CI/CD pipeline for AI
Returns: Pipeline status and key findings
Use when: Debugging CI failures with AI
Focus: Failed jobs, error messages, duration

Highlights:
- Failed job names and stages
- Error excerpts
- Performance issues

Related tools:
- gitlab_list_pipelines: Find pipelines
- gitlab_get_pipeline_job_log: Full logs"""

# Advanced Diff Tools
DESC_SMART_DIFF = """Get intelligent diff between refs
Returns: Structured diff with smart chunking
Use when: Need customizable diffs
Features: Context control, size limits

Advantages over standard diff:
- Configurable context lines
- File size filtering
- Better for large diffs

Related tools:
- gitlab_get_commit_diff: Simple commit diff
- gitlab_compare_refs: Basic comparison"""

DESC_SAFE_PREVIEW_COMMIT = """Preview commit without creating
Returns: What would change, validation results
Use when: Validating before actual commit
Shows: Affected files, potential errors

Safety features:
- No actual changes made
- Validates file paths
- Checks permissions

Related tools:
- gitlab_create_commit: Actual commit
- gitlab_list_repository_tree: Check files exist"""

# Batch Operations
DESC_BATCH_OPERATIONS = """Execute multiple operations atomically
Returns: Results of all operations or rollback
Use when: Complex multi-step workflows
Feature: Reference previous operation results

Key benefits:
- All-or-nothing execution
- Operation chaining
- Automatic rollback
- Result references: {{op1.field}}

Example workflow:
1. Create branch
2. Add files
3. Create MR
All succeed or all rolled back

Related tools:
- Individual operation tools
- gitlab_safe_preview_commit: Test first"""


# ============================================================================
# COMMON WORKFLOWS
# ============================================================================

WORKFLOW_CODE_REVIEW = """
Code Review Workflow:
1. gitlab_list_merge_requests - Find open MRs
2. gitlab_get_merge_request - Get MR details
3. gitlab_get_merge_request_changes - Review code changes
4. gitlab_get_merge_request_discussions - Read existing comments
5. gitlab_add_merge_request_comment - Provide feedback
6. gitlab_approve_merge_request - Approve when satisfied
7. gitlab_merge_merge_request - Merge approved MR
"""

WORKFLOW_CREATE_FEATURE = """
Feature Development Workflow:
1. gitlab_create_branch - Create feature branch
2. gitlab_create_commit - Add new code
3. gitlab_list_pipelines - Check CI status
4. gitlab_create_merge_request - Open MR for review
5. gitlab_update_merge_request - Add reviewers
"""

WORKFLOW_INVESTIGATE_BUG = """
Bug Investigation Workflow:
1. gitlab_get_issue - Read bug report
2. gitlab_list_commits - Check recent changes
3. gitlab_get_commit_diff - Review suspicious commits
4. gitlab_search_in_project - Search for related code
5. gitlab_add_issue_comment - Update findings
"""

# ============================================================================
# SNIPPET PARAMETER DESCRIPTIONS
# ============================================================================

DESC_SNIPPET_ID = """Snippet ID
Type: integer
Format: Numeric snippet identifier
Example: 123
How to find: From snippet URL or API responses"""

DESC_SNIPPET_TITLE = """Snippet title
Type: string
Format: Descriptive title for the snippet
Example: 'Database migration script'
Note: Required when creating snippets"""

DESC_SNIPPET_FILE_NAME = """Snippet file name
Type: string
Format: File name with extension
Example: 'migration.sql', 'helper.py', 'config.yaml'
Note: Used for syntax highlighting and display"""

DESC_SNIPPET_CONTENT = """Snippet content
Type: string
Format: Raw text content of the snippet
Example: 'console.log(\"Hello World\");'
Note: Can be code, text, or any content type"""

DESC_SNIPPET_DESCRIPTION = """Snippet description
Type: string
Format: Optional description of the snippet
Example: 'Helper script for database migrations'
Note: Provides context about the snippet's purpose"""

DESC_SNIPPET_VISIBILITY = """Snippet visibility
Type: string
Format: Visibility level for the snippet
Options: 'private' | 'internal' | 'public'
Default: 'private'
Examples:
  - 'private' (only visible to author)
  - 'internal' (visible to authenticated users)
  - 'public' (visible to everyone)"""

# ============================================================================
# SNIPPET TOOL DESCRIPTIONS
# ============================================================================

DESC_LIST_SNIPPETS = """List project snippets
Returns: Array of snippets with metadata
Use when: Browsing code snippets, finding reusable code
Pagination: Yes (default 20 per page)
Filtering: By project

Example response:
[{
  "id": 123,
  "title": "Database Helper",
  "file_name": "db_helper.py",
  "description": "Common database operations",
  "visibility": "private",
  "author": {"name": "John Doe"},
  "created_at": "2023-01-01T00:00:00Z",
  "web_url": "https://gitlab.com/group/project/snippets/123"
}]

Related tools:
- gitlab_get_snippet: Get snippet content
- gitlab_create_snippet: Create new snippet"""

DESC_GET_SNIPPET = """Get snippet details and content
Returns: Complete snippet information with content
Use when: Reading snippet code, reviewing implementations
Content: Full text content included

Example response:
{
  "id": 123,
  "title": "API Helper Functions",
  "file_name": "api_helpers.js",
  "content": "function fetchData(url) { ... }",
  "description": "Common API utility functions",
  "visibility": "internal",
  "author": {"name": "Jane Smith"},
  "created_at": "2023-01-01T00:00:00Z",
  "web_url": "https://gitlab.com/group/project/snippets/123"
}

Related tools:
- gitlab_list_snippets: Browse available snippets
- gitlab_update_snippet: Modify snippet"""

DESC_CREATE_SNIPPET = """Create a new code snippet
Creates: New snippet with specified content and metadata
Use when: Saving reusable code, sharing solutions, documenting examples
Required: title, file_name, content
Optional: description, visibility

Example usage:
{
  "title": "Docker Compose Template",
  "file_name": "docker-compose.yml",
  "content": "version: '3.8'\\nservices:\\n  app:\\n    image: nginx",
  "description": "Basic Docker Compose setup",
  "visibility": "internal"
}

Returns: Created snippet with ID and URLs

Related tools:
- gitlab_update_snippet: Modify after creation
- gitlab_list_snippets: View created snippets"""

DESC_UPDATE_SNIPPET = """Update existing snippet
Modifies: Title, content, file name, description, or visibility
Use when: Fixing code, updating examples, changing permissions
Flexibility: Update any combination of fields

Example usage:
{
  "snippet_id": 123,
  "title": "Updated API Helper",
  "content": "// Updated with error handling\\nfunction fetchData(url) { ... }",
  "description": "Enhanced with proper error handling"
}

Returns: Updated snippet information

Related tools:
- gitlab_get_snippet: View current content before updating
- gitlab_create_snippet: Create new instead of updating"""

# ============================================================================
# JOB AND ARTIFACT PARAMETER DESCRIPTIONS
# ============================================================================

DESC_PIPELINE_ID = """Pipeline ID
Type: integer
Format: Numeric pipeline identifier
Example: 12345
How to find: From pipeline URLs or gitlab_list_pipelines response"""

DESC_JOB_ID = """Job ID  
Type: integer
Format: Numeric job identifier
Example: 67890
How to find: From job URLs or gitlab_list_pipeline_jobs response"""

DESC_ARTIFACT_PATH = """Artifact path
Type: string
Format: Path to specific artifact file within job artifacts
Example: 'dist/bundle.js', 'reports/coverage.xml'
Optional: If not specified, returns info about all artifacts"""

DESC_JOB_SCOPE = """Job scope filter
Type: string
Format: Filter jobs by status
Options: 'created' | 'pending' | 'running' | 'failed' | 'success' | 'canceled' | 'skipped' | 'waiting_for_resource' | 'manual'
Examples:
  - 'failed' (only failed jobs)
  - 'success' (only successful jobs)
  - 'running' (currently running jobs)"""

# ============================================================================
# JOB AND ARTIFACT TOOL DESCRIPTIONS
# ============================================================================

DESC_LIST_PIPELINE_JOBS = """List jobs in a specific pipeline
Returns: Array of jobs with status, timing, and artifact information
Use when: Debugging pipeline failures, checking job status, finding artifacts
Pagination: Yes (default 20 per page)
Details: Includes job stage, status, duration, runner info

Example response:
[{
  "id": 12345,
  "name": "test:unit",
  "stage": "test", 
  "status": "success",
  "created_at": "2023-01-01T10:00:00Z",
  "duration": 120.5,
  "artifacts": [{"filename": "coverage.xml"}],
  "web_url": "https://gitlab.com/group/project/-/jobs/12345"
}]

Related tools:
- gitlab_list_pipelines: Find pipeline IDs
- gitlab_download_job_artifact: Get job artifacts"""

DESC_DOWNLOAD_JOB_ARTIFACT = """Get information about job artifacts
Returns: Artifact metadata and download information
Use when: Checking build outputs, downloading test results, accessing reports
Security: Returns artifact info only (no actual file download for security)
Content: Lists available artifacts with sizes and expiration

Example response:
{
  "job_id": 12345,
  "job_name": "build:production",
  "artifacts": [
    {"filename": "dist.zip", "size": 1024000},
    {"filename": "reports/junit.xml", "size": 5120}
  ],
  "artifacts_expire_at": "2023-02-01T00:00:00Z",
  "download_note": "Use GitLab web interface or CLI for actual downloads"
}

Related tools:
- gitlab_list_pipeline_jobs: Find job IDs with artifacts
- gitlab_list_project_jobs: Browse all project jobs"""

DESC_LIST_PROJECT_JOBS = """List all jobs for a project
Returns: Array of jobs across all pipelines with filtering options
Use when: Monitoring project CI/CD, finding recent failures, browsing job history
Pagination: Yes (default 20 per page)
Filtering: By job status/scope (failed, success, running, etc.)

Example response:
[{
  "id": 67890,
  "name": "deploy:staging",
  "stage": "deploy",
  "status": "failed", 
  "pipeline": {"id": 123, "ref": "main"},
  "commit": {"short_id": "abc1234"},
  "created_at": "2023-01-01T15:30:00Z",
  "user": {"name": "Jane Doe"}
}]

Related tools:
- gitlab_list_pipeline_jobs: Jobs for specific pipeline
- gitlab_list_pipelines: Find pipeline information"""
