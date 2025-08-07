"""Common descriptions and parameter definitions for GitLab tools"""

# Common parameter descriptions
DESC_PER_PAGE = "Number of results per page (integer, 1-100, default: 20)"
DESC_PAGE_NUMBER = "Page number for pagination (integer, ≥1, default: 1)"
DESC_PROJECT_ID = "Project ID (integer) or path (string like 'group/project'). Optional - auto-detects from current git repository if not provided"
DESC_PROJECT_ID_REQUIRED = "Project ID (integer) or full path (string). Required. Format: 'namespace/project' or numeric ID"
DESC_SEARCH_TERM = "Search query string. Searches in project names and descriptions. Case-insensitive partial matching"
DESC_REF = "Git reference: branch name, tag name, or commit SHA. Optional - defaults to project's default branch (usually 'main' or 'master')"
DESC_STATE_ISSUE = "Filter by issue state (string). Options: 'opened', 'closed', 'all'. Default: 'all'"
DESC_STATE_MR = "Filter by merge request state (string). Options: 'opened', 'closed', 'merged', 'all'. Default: 'all'"
DESC_ISSUE_IID = "Issue internal ID (integer). Project-specific issue number (e.g., #123). Not the global issue ID"
DESC_MR_IID = "Merge request internal ID (integer). Project-specific MR number (e.g., !456). Not the global MR ID"
DESC_FILE_PATH = "File path in repository (string). Use forward slashes. Example: 'src/main.py' or 'docs/README.md'"
DESC_TREE_PATH = "Directory path in repository (string). Use forward slashes. Empty string for root. Example: 'src/components'"
DESC_COMMIT_SHA = "Git commit SHA (string). Can be abbreviated (min 7 chars) or full 40-character SHA"
DESC_USERNAME = "GitLab username (string). The @username without the @ symbol. Case-sensitive"
DESC_OWNED_PROJECTS = "Filter to show only owned projects (boolean). True = only projects you own. Default: false"
DESC_GIT_PATH = "Path to local git repository (string). Absolute or relative path. Default: '.' (current directory)"
DESC_SORT_ORDER = "Sort direction (string). Options: 'asc' (ascending), 'desc' (descending). Default varies by context"
DESC_ORDER_BY = "Field to sort results by (string). Options vary by endpoint (e.g., 'created_at', 'updated_at', 'name')"
DESC_MAX_BODY_LENGTH = "Maximum characters for comment/note bodies (integer). 0 = unlimited. Default: 1000. Truncates with '...' if exceeded"
DESC_RECURSIVE = "Include subdirectories recursively (boolean). True = traverse all subdirectories. Default: false"
DESC_DATE_SINCE = "Start date for filtering (string, ISO 8601 format). Example: '2024-01-01' or '2024-01-01T00:00:00Z'"
DESC_DATE_UNTIL = "End date for filtering (string, ISO 8601 format). Example: '2024-12-31' or '2024-12-31T23:59:59Z'"
DESC_PATH_FILTER = "Filter commits affecting this file path (string). Shows only commits that modified this file. Example: 'src/main.py'"
DESC_INCLUDE_STATS = "Include commit statistics (boolean). Adds additions/deletions/total change counts. Default: false"
DESC_SEARCH_SCOPE = "Scope to search within (string). Options: 'issues', 'merge_requests', 'milestones', 'wiki_blobs', 'commits', 'blobs', 'users'"
DESC_BRANCH_TAG_REF = "Branch or tag name to filter by (string). Example: 'main', 'develop', 'v1.0.0'"
DESC_ACTION_FILTER = "Filter events by action type (string). Options: 'created', 'updated', 'closed', 'reopened', 'pushed', 'commented', 'merged', 'joined', 'left', 'destroyed', 'expired'"
DESC_TARGET_TYPE_FILTER = "Filter events by target type (string). Options: 'Issue', 'MergeRequest', 'Milestone', 'Note', 'Project', 'Snippet', 'User'"
DESC_DATE_AFTER = "Get events after this date (string, ISO 8601). Inclusive. Example: '2024-01-01' or '2024-01-01T00:00:00Z'"
DESC_DATE_BEFORE = "Get events before this date (string, ISO 8601). Inclusive. Example: '2024-12-31' or '2024-12-31T23:59:59Z'"

# Additional parameter descriptions
DESC_TITLE = "Title text (string, required for create/update). Max 255 characters. Supports emoji and special characters"
DESC_DESCRIPTION = "Description body (string, markdown supported). Can include mentions (@user), references (#123, !456), and task lists"
DESC_ASSIGNEE_ID = "User ID to assign (integer). Use user's numeric GitLab ID, not username. Single assignee only"
DESC_ASSIGNEE_IDS = "Array of user IDs to assign (array of integers). Multiple assignees supported. Example: [123, 456]"
DESC_REVIEWER_IDS = "Array of user IDs to request review from (array of integers). MR reviewers. Example: [789, 012]"
DESC_LABELS = "Labels to apply (string, comma-separated). Example: 'bug,priority:high,frontend'. Creates new labels if needed"
DESC_MILESTONE_ID = "Milestone ID to associate (integer). Must be an existing milestone in the project. Use null to unset"
DESC_STATE_EVENT = "State transition action (string). Options: 'close' (close issue/MR), 'reopen' (reopen closed issue/MR)"
DESC_REMOVE_SOURCE_BRANCH = "Delete source branch after merge (boolean). Cleans up feature branches. Default: false. Requires permissions"
DESC_SQUASH = "Squash commits on merge (boolean). Combines all commits into one. Default: follows project settings"
DESC_DISCUSSION_LOCKED = "Lock discussion threads (boolean). Prevents new comments except by project members. Default: false"
DESC_ALLOW_COLLABORATION = "Allow commits from upstream members (boolean). Lets maintainers push to fork's branch. Default: true"
DESC_TARGET_BRANCH = "Target branch for merge (string, required). The branch to merge into. Example: 'main' or 'develop'"
DESC_MERGE_WHEN_PIPELINE_SUCCEEDS = "Auto-merge when pipeline succeeds (boolean). Merges automatically after CI passes. Default: false"
DESC_MERGE_COMMIT_MESSAGE = "Custom merge commit message (string). Overrides default merge message. Supports variables like %{title}"
DESC_SQUASH_COMMIT_MESSAGE = "Custom squash commit message (string). Message for squashed commit. Supports variables like %{title}"
DESC_COMMENT_BODY = "Comment text content (string, required). Supports markdown, mentions (@user), and references (#123, !456)"
DESC_FROM_REF = "Source ref for comparison (string, required). Branch name, tag, or commit SHA to compare from"
DESC_TO_REF = "Target ref for comparison (string, required). Branch name, tag, or commit SHA to compare to"
DESC_STRAIGHT = "Use straight diff instead of three-dot (boolean). True = direct diff, False = merge-base diff. Default: false"
DESC_ORDER_BY_TAG = "Field to order tags by (string). Options: 'name' (alphabetical), 'updated' (last updated), 'version', 'semver' (semantic version). Default: 'updated'"
DESC_BRANCH = "Git branch name (string, required). Target branch for commits. Must exist. Example: 'feature/new-feature'"
DESC_COMMIT_MESSAGE = "Commit message (string, required). Follows conventional commits format. First line = summary (50 chars), blank line, then body"
DESC_ACTIONS = "Array of file operations (array of objects, required). Each action: {action: 'create'|'update'|'delete'|'move', file_path: string, content?: string}"
DESC_AUTHOR_EMAIL = "Commit author email (string, optional). Overrides authenticated user's email. Must be valid email format"
DESC_AUTHOR_NAME = "Commit author name (string, optional). Overrides authenticated user's name. Any valid string"
DESC_QUERY = "Search query text (string). Searches usernames, names, and emails. Partial matching, case-insensitive"
DESC_DISCUSSION_ID = "Discussion thread ID (string, required). Get from merge_request_discussions response. Format: SHA-like string"
DESC_PIPELINE_ID = "Pipeline ID (integer). Specific pipeline run identifier. Get from list_pipelines"
DESC_MAX_LENGTH = "Maximum summary length in characters (integer). AI summaries will be truncated to fit. Default: 500"
DESC_CONTEXT_LINES = "Number of unchanged lines to show around changes in diff (integer). Default: 3. Range: 0-10"
DESC_MAX_FILE_SIZE = "Maximum file size in bytes to include in diff (integer). Files larger are skipped. Default: 50000 (50KB)"
DESC_OPERATIONS = "Array of operations to execute in sequence (array of objects, required). Each: {name: string, tool: string, arguments: object}"
DESC_STOP_ON_ERROR = "Stop batch execution on first error (boolean). True = fail fast with rollback, False = continue and collect errors. Default: true"

# Tool descriptions
DESC_LIST_PROJECTS = "List GitLab projects accessible to you. Filter by ownership, search by name/description, and paginate results (default 20 per page). Returns project ID, name, description, URLs, and basic stats."
DESC_GET_PROJECT = "Get comprehensive details of a specific GitLab project by ID or path (e.g., 'group/project'). Returns full project metadata including settings, permissions, statistics, and configuration."
DESC_DETECT_PROJECT = "Detect GitLab project from current git repository"  # Deprecated
DESC_GET_CURRENT_PROJECT = "Auto-detect and retrieve GitLab project information from the current git repository. Examines git remotes to find associated GitLab project. Returns same details as get_project."
DESC_LIST_ISSUES = "List issues in a GitLab project with filtering by state (opened/closed/all), pagination support (default 20 per page), and full issue details including labels, assignees, and timestamps."
DESC_GET_ISSUE = "Get complete details of a specific issue by its IID (internal ID). Returns title, description, state, labels, assignees, milestone, time tracking, related MRs, and all metadata."
DESC_LIST_MRS = "List merge requests in a project filtered by state (opened/closed/merged/all), with pagination (default 20 per page). Returns MR details including source/target branches, approval status, and pipeline info."
DESC_GET_MR = "Get comprehensive details of a specific merge request by IID. Returns complete MR data including diff stats, approval status, pipeline status, merge status, conflicts, and all metadata."
DESC_GET_MR_NOTES = "List all comments/notes on a merge request including discussions, code reviews, and system notes. Sort by creation/update time, paginate results, and optionally truncate long comment bodies."
DESC_GET_FILE_CONTENT = "Retrieve raw content of a file from the repository at a specific ref (branch/tag/commit SHA). Returns the file content as a string. Useful for reading source code, configs, or documentation."
DESC_GET_TREE = "Browse repository structure (files and directories)"  # Deprecated
DESC_LIST_TREE = "Browse repository file structure at a specific path and ref (branch/tag/commit). Returns file and directory listings with type, mode, and SHA. Supports recursive traversal option."
DESC_GET_COMMITS = "Get commit history for a project with pagination and filtering"  # Deprecated
DESC_LIST_COMMITS = "List commit history for a project or specific branch/tag. Filter by date range (since/until), file path, author, and paginate results. Returns commit SHA, message, author, timestamp, and stats."
DESC_GET_COMMIT = "Get full details of a specific commit by SHA including message, author, committer, parent SHAs, stats (additions/deletions), and GPG signature verification status."
DESC_GET_COMMIT_DIFF = "Get the complete diff of changes introduced by a commit. Returns modified files with full diff content showing added/removed lines. Useful for code review."
DESC_SEARCH_PROJECTS = "Search for projects across all of GitLab by name or description. Returns matching projects with basic info. More comprehensive than list_projects' search which only searches your accessible projects."
DESC_SEARCH_IN_PROJECT = "Search within a project's issues, merge requests, commits, wiki pages, and more. Specify scope (issues/merge_requests/milestones/wiki_blobs/commits/blobs/users) and search query."
DESC_LIST_BRANCHES = "List all branches in a project with their latest commit info. Filter by search term to find specific branches. Returns branch name, commit SHA, protected status, and whether it can be deleted."
DESC_LIST_PIPELINES = "List CI/CD pipeline runs for a project, filtered by status (running/pending/success/failed/canceled/skipped) and branch. Returns pipeline ID, status, ref, SHA, and timing information."
DESC_GET_USER_EVENTS = "Get activity events for a GitLab user with pagination"  # Deprecated
DESC_LIST_USER_EVENTS = "Get a user's GitLab activity feed including commits, comments, issues, MRs, and more. Filter by action type and target type. Returns event details with timestamps and context."

# MR lifecycle tool descriptions
DESC_UPDATE_MR = "Update any modifiable field of a merge request: title, description, target branch, assignees, reviewers, labels, milestone, or state. Supports closing/reopening and draft status."
DESC_CLOSE_MR = "Close an open merge request without merging. The MR can be reopened later. Useful for abandoning changes or deferring work. Returns updated MR with closed status."
DESC_MERGE_MR = "Merge an approved MR into its target branch. Options: squash commits, delete source branch after merge, custom merge commit message, and merge when pipeline succeeds."

# Comment tool descriptions
DESC_ADD_ISSUE_COMMENT = "Post a new comment on an issue. Supports markdown formatting, mentions (@username), and references to other issues/MRs. Returns the created comment with metadata."
DESC_ADD_MR_COMMENT = "Post a new comment on a merge request discussion thread. Supports markdown, code blocks, mentions, and references. Returns the created note with author and timestamp."

# Approval tool descriptions
DESC_APPROVE_MR = "Add your approval to a merge request. Required for MRs with approval rules. Note: you cannot approve your own MRs. Returns approval status after action."
DESC_GET_MR_APPROVALS = "Check approval status of an MR including required approvals, approval rules, approved_by list, and whether MR meets approval requirements for merging."

# Repository tool descriptions
DESC_GET_TAGS = "List tags in a project with ordering options"  # Deprecated
DESC_LIST_TAGS = "List all git tags in a project. Order by name, update time, version, or semantic version. Returns tag name, commit SHA, message, and release info if available."
DESC_CREATE_COMMIT = "Create a new commit with multiple file operations in a single atomic transaction. Supports create/update/delete/move actions. Specify branch, commit message, and author details."
DESC_COMPARE_REFS = "Compare two refs (branches/tags/commits) to see differences. Returns commit list, diff stats, and file changes. Useful for reviewing changes before merging or creating MRs."

# Release and member tool descriptions
DESC_LIST_RELEASES = "List GitLab releases (not just tags) with release notes, assets, and links. Order by release date or creation date. Returns version, description, author, and asset details."
DESC_GET_PROJECT_MEMBERS = "Get project members with search and pagination"  # Deprecated
DESC_LIST_PROJECT_MEMBERS = "List project members including inherited members from parent groups. Search by username/name, view access levels (Guest/Reporter/Developer/Maintainer/Owner), and member details."
DESC_GET_PROJECT_HOOKS = "List project webhooks"  # Deprecated
DESC_LIST_PROJECT_HOOKS = "List all configured webhooks for a project showing URL, triggers (push/issues/MR/wiki events), token presence, SSL verification, and enablement status."

# MR advanced tool descriptions
DESC_GET_MR_DISCUSSIONS = "List all discussion threads on an MR including code review comments, general discussions, and resolved threads. Returns nested structure with notes and metadata."
DESC_RESOLVE_DISCUSSION = "Mark a discussion thread as resolved. Typically used when code review feedback has been addressed. Requires discussion ID from get_merge_request_discussions."
DESC_GET_MR_CHANGES = "Get detailed file changes in an MR including full diffs, file paths, addition/deletion counts, and change types (added/modified/deleted). Similar to commit diff but for entire MR."

# MR operations tool descriptions
DESC_REBASE_MR = "Rebase the source branch of an MR onto the latest target branch HEAD. Resolves out-of-date status. Requires developer access and fast-forward merge method."
DESC_CHERRY_PICK = "Apply a specific commit to another branch without merging. Creates a new commit on target branch. Useful for backporting fixes or selective change application."

# AI helper tool descriptions
DESC_SUMMARIZE_MR = "Generate a concise, AI-optimized summary of an MR including title, description, changes overview, discussions, and approval status. Length-limited for LLM context efficiency."
DESC_SUMMARIZE_ISSUE = "Create a condensed summary of an issue with title, description, comments, labels, and status. Intelligently truncates long content while preserving key information."
DESC_SUMMARIZE_PIPELINE = "Summarize CI/CD pipeline execution including status, duration, failed jobs, test results, and artifacts. Focuses on actionable information for debugging failures."

# Advanced diff tool descriptions
DESC_SMART_DIFF = "Retrieve diff between refs with intelligent chunking, configurable context lines, and size limits. Returns structured hunks suitable for code review. Handles large diffs gracefully."
DESC_SAFE_PREVIEW_COMMIT = "Simulate a commit to preview resulting changes without modifying the repository. Validates file operations and shows what would change. Useful for verification before actual commit."

# Batch operations tool description
DESC_BATCH_OPERATIONS = "Execute multiple GitLab operations as an atomic transaction. Supports operation chaining with result references ({{op1.field}}). Automatic rollback on failure ensures consistency."