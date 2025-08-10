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
TOOL_GET_CURRENT_USER = "gitlab_get_current_user"
TOOL_GET_USER = "gitlab_get_user"

# New renamed tools
TOOL_LIST_COMMITS = "gitlab_list_commits"
TOOL_LIST_REPOSITORY_TREE = "gitlab_list_repository_tree"
TOOL_LIST_TAGS = "gitlab_list_tags"
TOOL_LIST_USER_EVENTS = "gitlab_list_user_events"
TOOL_LIST_PROJECT_MEMBERS = "gitlab_list_project_members"
TOOL_LIST_PROJECT_HOOKS = "gitlab_list_project_hooks"
TOOL_LIST_RELEASES = "gitlab_list_releases"

# Group tools
TOOL_LIST_GROUPS = "gitlab_list_groups"
TOOL_GET_GROUP = "gitlab_get_group"
TOOL_LIST_GROUP_PROJECTS = "gitlab_list_group_projects"

# Snippets tools
TOOL_LIST_SNIPPETS = "gitlab_list_snippets"
TOOL_GET_SNIPPET = "gitlab_get_snippet"
TOOL_CREATE_SNIPPET = "gitlab_create_snippet"
TOOL_UPDATE_SNIPPET = "gitlab_update_snippet"

# Job and Artifact tools
TOOL_LIST_PIPELINE_JOBS = "gitlab_list_pipeline_jobs"
TOOL_DOWNLOAD_JOB_ARTIFACT = "gitlab_download_job_artifact"
TOOL_LIST_PROJECT_JOBS = "gitlab_list_project_jobs"

# Single-resource getters
TOOL_GET_ISSUE = "gitlab_get_issue"
TOOL_GET_MERGE_REQUEST = "gitlab_get_merge_request"
TOOL_GET_FILE_CONTENT = "gitlab_get_file_content"
TOOL_GET_COMMIT = "gitlab_get_commit"
TOOL_GET_COMMIT_DIFF = "gitlab_get_commit_diff"
TOOL_GET_MR_APPROVALS = "gitlab_get_merge_request_approvals"
TOOL_GET_MR_DISCUSSIONS = "gitlab_get_merge_request_discussions"
TOOL_GET_MR_CHANGES = "gitlab_get_merge_request_changes"

# Search tools
TOOL_SEARCH_PROJECTS = "gitlab_search_projects"
TOOL_SEARCH_IN_PROJECT = "gitlab_search_in_project"

# Action-oriented tools
TOOL_UPDATE_MR = "gitlab_update_merge_request"
TOOL_CLOSE_MR = "gitlab_close_merge_request"
TOOL_MERGE_MR = "gitlab_merge_merge_request"
TOOL_REBASE_MR = "gitlab_rebase_merge_request"
TOOL_APPROVE_MR = "gitlab_approve_merge_request"
TOOL_ADD_ISSUE_COMMENT = "gitlab_add_issue_comment"
TOOL_ADD_MR_COMMENT = "gitlab_add_merge_request_comment"
TOOL_RESOLVE_DISCUSSION = "gitlab_resolve_discussion"
TOOL_CREATE_COMMIT = "gitlab_create_commit"
TOOL_CHERRY_PICK_COMMIT = "gitlab_cherry_pick_commit"
TOOL_COMPARE_REFS = "gitlab_compare_refs"

# AI and Advanced Tools
TOOL_SUMMARIZE_MR = "gitlab_summarize_merge_request"
TOOL_SUMMARIZE_ISSUE = "gitlab_summarize_issue"
TOOL_SUMMARIZE_PIPELINE = "gitlab_summarize_pipeline"
TOOL_SMART_DIFF = "gitlab_smart_diff"
TOOL_SAFE_PREVIEW_COMMIT = "gitlab_safe_preview_commit"
TOOL_BATCH_OPERATIONS = "gitlab_batch_operations"

# User & Profile tools
TOOL_SEARCH_USER = "gitlab_search_user"
TOOL_GET_USER_DETAILS = "gitlab_get_user_details"
TOOL_GET_MY_PROFILE = "gitlab_get_my_profile"
TOOL_GET_USER_CONTRIBUTIONS_SUMMARY = "gitlab_get_user_contributions_summary"
TOOL_GET_USER_ACTIVITY_FEED = "gitlab_get_user_activity_feed"

# User's Issues & MRs tools
TOOL_GET_USER_OPEN_MRS = "gitlab_get_user_open_mrs"
TOOL_GET_USER_REVIEW_REQUESTS = "gitlab_get_user_review_requests"
TOOL_GET_USER_OPEN_ISSUES = "gitlab_get_user_open_issues"
TOOL_GET_USER_REPORTED_ISSUES = "gitlab_get_user_reported_issues"
TOOL_GET_USER_RESOLVED_ISSUES = "gitlab_get_user_resolved_issues"

# User's Code & Commits tools
TOOL_GET_USER_COMMITS = "gitlab_get_user_commits"
TOOL_GET_USER_MERGE_COMMITS = "gitlab_get_user_merge_commits"
TOOL_GET_USER_CODE_CHANGES_SUMMARY = "gitlab_get_user_code_changes_summary"
TOOL_GET_USER_SNIPPETS = "gitlab_get_user_snippets"

# User's Comments & Discussions tools
TOOL_GET_USER_ISSUE_COMMENTS = "gitlab_get_user_issue_comments"
TOOL_GET_USER_MR_COMMENTS = "gitlab_get_user_mr_comments"
TOOL_GET_USER_DISCUSSION_THREADS = "gitlab_get_user_discussion_threads"
TOOL_GET_USER_RESOLVED_THREADS = "gitlab_get_user_resolved_threads"

# Me / Inbox tools
TOOL_GET_MY_OPEN_MRS = "gitlab_get_my_open_mrs"
TOOL_GET_MRS_AWAITING_MY_REVIEW = "gitlab_get_mrs_awaiting_my_review"
TOOL_GET_MY_OPEN_ISSUES = "gitlab_get_my_open_issues"
TOOL_GET_MY_TODOS_DIGEST = "gitlab_get_my_todos_digest"

# MR Triage & Review Flow tools
TOOL_FIND_REVIEW_READY_MRS = "gitlab_find_review_ready_mrs"
TOOL_FIND_STALE_MRS = "gitlab_find_stale_mrs"
TOOL_FIND_MERGE_BLOCKERS = "gitlab_find_merge_blockers"
TOOL_AUTOFIX_MR_METADATA = "gitlab_autofix_mr_metadata"
TOOL_ASSIGN_REVIEWER_ROTATION = "gitlab_assign_reviewer_rotation"
TOOL_AUTO_MERGE_WHEN_GREEN = "gitlab_auto_merge_when_green"
TOOL_RESOLVE_DISCUSSIONS_AND_MERGE = "gitlab_resolve_discussions_and_merge"

# Issue ↔ Branch ↔ MR Workflow tools
TOOL_BOOTSTRAP_ISSUE_BRANCH_MR = "gitlab_bootstrap_issue_branch_mr"
TOOL_LINK_ISSUE_TO_EXISTING_MR = "gitlab_link_issue_to_existing_mr"
TOOL_BULK_CLOSE_FIXED_ISSUES = "gitlab_bulk_close_fixed_issues"

# Release & Backports tools
TOOL_PREPARE_RELEASE_NOTES = "gitlab_prepare_release_notes"
TOOL_TAG_AND_RELEASE_FROM_MILESTONE = "gitlab_tag_and_release_from_milestone"
TOOL_BACKPORT_MR_TO_BRANCHES = "gitlab_backport_mr_to_branches"
TOOL_HOTFIX_FROM_ISSUE = "gitlab_hotfix_from_issue"

# CI/CD & Quality tools
TOOL_RERUN_FAILED_PIPELINE_SEGMENT = "gitlab_rerun_failed_pipeline_segment"
TOOL_FLAKY_TEST_DETECTOR = "gitlab_flaky_test_detector"
TOOL_PIPELINE_RED_ALERTS = "gitlab_pipeline_red_alerts"
TOOL_DOWNLOAD_LATEST_ARTIFACTS = "gitlab_download_latest_artifacts"
TOOL_COMPARE_PIPELINE_DURATIONS = "gitlab_compare_pipeline_durations"

# Code & Security tools
TOOL_SMART_CODE_SEARCH = "gitlab_smart_code_search"
TOOL_FIND_SUSPECT_COMMITS_SINCE_FAILURE = "gitlab_find_suspect_commits_since_failure"
TOOL_DEPENDENCY_UPDATE_BATCH = "gitlab_dependency_update_batch"
TOOL_SECURITY_FINDINGS_DIGEST = "gitlab_security_findings_digest"

# Project Hygiene tools
TOOL_PRUNE_STALE_BRANCHES = "gitlab_prune_stale_branches"
TOOL_SYNC_LABELS_POLICY = "gitlab_sync_labels_policy"
TOOL_AUTO_ARCHIVE_OLD_ISSUES = "gitlab_auto_archive_old_issues"
TOOL_ENFORCE_MR_RULESET = "gitlab_enforce_mr_ruleset"

# Cross-Project Views tools
TOOL_GROUP_MR_RISK_RADAR = "gitlab_group_mr_risk_radar"
TOOL_GROUP_ACTIVITY_SUMMARY = "gitlab_group_activity_summary"
TOOL_GROUP_OPEN_RELEASE_TRAINS = "gitlab_group_open_release_trains"

# Ownership & Notifications tools
TOOL_OWNER_MAP_FROM_CODEOWNERS = "gitlab_owner_map_from_codeowners"
TOOL_NOTIFY_OWNERS_ON_DIRECTORY_CHANGES = "gitlab_notify_owners_on_directory_changes"

# Governance & Compliance tools
TOOL_MR_TEMPLATE_ENFORCER = "gitlab_mr_template_enforcer"
TOOL_LICENCE_COMPLIANCE_AUDIT = "gitlab_licence_compliance_audit"
