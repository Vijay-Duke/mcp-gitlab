# MCP GitLab Server

[![CI](https://github.com/Vijay-Duke/mcp-gitlab/actions/workflows/ci.yml/badge.svg)](https://github.com/Vijay-Duke/mcp-gitlab/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Vijay-Duke/mcp-gitlab/branch/main/graph/badge.svg)](https://codecov.io/gh/Vijay-Duke/mcp-gitlab)
[![Documentation Status](https://readthedocs.org/projects/mcp-gitlab/badge/?version=latest)](https://mcp-gitlab.readthedocs.io/en/latest/?badge=latest)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://opensource.org/licenses/Apache-2.0)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://github.com/anthropics/mcp)

A Model Context Protocol (MCP) server that provides comprehensive GitLab API integration. This server enables LLMs to interact with GitLab repositories, manage merge requests, issues, and perform various Git operations.

<a href="https://glama.ai/mcp/servers/@Vijay-Duke/mcp-gitlab">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@Vijay-Duke/mcp-gitlab/badge" alt="GitLab Server MCP server" />
</a>

## Features

### Core Features
- 🔐 **Authentication & Users** - Get current user info and lookup user profiles
- 🔍 **Project Management** - List, search, and get details about GitLab projects
- 📝 **Issues** - List, read, search, and comment on issues
- 🔀 **Merge Requests** - List, read, update, approve, and merge MRs
- 📁 **Repository Files** - Browse, read, and commit changes to files
- 🌳 **Branches & Tags** - List and manage branches and tags
- 🔧 **CI/CD Pipelines** - View pipeline status, jobs, and artifacts
- 💬 **Discussions** - Read and resolve merge request discussions
- 🎯 **Smart Operations** - Batch operations, AI summaries, and smart diffs

### Advanced Features
- **Batch Operations** - Execute multiple GitLab operations atomically with rollback support
- **AI-Optimized Summaries** - Generate concise summaries of MRs, issues, and pipelines
- **Smart Diffs** - Get structured diffs with configurable context and size limits
- **Safe Preview** - Preview file changes before committing
- **Cross-Reference Support** - Reference results from previous operations in batch mode

## Installation

### Using uvx (recommended - no installation needed)

```bash
# Run directly without installation
uvx mcp-gitlab
```

### From source

```bash
# Clone the repository
git clone https://github.com/Vijay-Duke/mcp-gitlab.git
cd mcp-gitlab

# Install dependencies and run with uv
uv sync
uv run mcp-gitlab

# Or install in development mode with test dependencies
uv sync --all-extras
uv run pytest  # to run tests
```

## Configuration

### Environment Variables

Set one of the following authentication tokens:

```bash
# Private token (recommended for personal use)
export GITLAB_PRIVATE_TOKEN="your-private-token"

# OAuth token
export GITLAB_OAUTH_TOKEN="your-oauth-token"

# GitLab URL (optional, defaults to https://gitlab.com)
export GITLAB_URL="https://gitlab.example.com"
```

### Getting a GitLab Token

1. Go to your GitLab profile settings
2. Navigate to "Access Tokens"
3. Create a new token with the following scopes:
   - `api` - Full API access
   - `read_repository` - Read repository content
   - `write_repository` - Write repository content (for commits)

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration:

#### Using uvx (recommended - no installation needed):

```json
{
  "mcp-gitlab": {
    "command": "uvx",
    "args": ["mcp-gitlab"],
    "env": {
      "GITLAB_PRIVATE_TOKEN": "your-token-here"
    }
  }
}
```

#### Using uv (if you've cloned the repository):

```json
{
  "mcp-gitlab": {
    "command": "uv",
    "args": ["run", "mcp-gitlab"],
    "cwd": "/path/to/mcp-gitlab",
    "env": {
      "GITLAB_PRIVATE_TOKEN": "your-token-here"
    }
  }
}
```

Replace `/path/to/mcp-gitlab` with the full path to where you cloned the repository.

### Running with uvx

The easiest way to run the MCP GitLab server is using `uvx`:

```bash
# Set your GitLab token
export GITLAB_PRIVATE_TOKEN="your-token-here"

# Run the server directly with uvx
uvx mcp-gitlab
```

### Standalone Usage

```bash
# If running from source (after uv sync)
uv run mcp-gitlab

# Or run the Python module directly
uv run python -m mcp_gitlab
```

## Available Tools

### Authentication & User Info

#### `gitlab_get_current_user`
Get the currently authenticated user's profile information.
```json
{}
```

Returns comprehensive information including:
- Basic info: ID, username, name, email
- Profile details: bio, organization, job title
- Account status: state, creation date, admin status
- Permissions: can_create_group, can_create_project
- Security: two_factor_enabled, external status

#### `gitlab_get_user`
Get details for a specific user by ID or username.
```json
{
  "user_id": 12345
}
```
or
```json
{
  "username": "johndoe"
}
```

Returns user information including:
- Basic info: ID, username, name
- Profile: avatar_url, web_url, bio
- Organization details: company, job title
- Account status and creation date

### Project Management

#### `gitlab_list_projects`
List accessible GitLab projects with pagination and search.
```json
{
  "owned": false,
  "search": "my-project",
  "per_page": 20,
  "page": 1
}
```

#### `gitlab_get_project`
Get detailed information about a specific project.
```json
{
  "project_id": "group/project"
}
```

#### `gitlab_get_current_project`
Get the GitLab project information from the current git repository.
```json
{
  "path": "."
}
```

### Issues

#### `gitlab_list_issues`
List project issues with state filtering.
```json
{
  "project_id": "group/project",
  "state": "opened",
  "per_page": 20
}
```

#### `gitlab_get_issue`
Get a single issue with full details.
```json
{
  "project_id": "group/project",
  "issue_iid": 123
}
```

#### `gitlab_add_issue_comment`
Add a comment to an issue.
```json
{
  "project_id": "group/project",
  "issue_iid": 123,
  "body": "Thanks for reporting this!"
}
```

### Merge Requests

#### `gitlab_list_merge_requests`
List merge requests with filtering options.
```json
{
  "project_id": "group/project",
  "state": "opened"
}
```

#### `gitlab_get_merge_request`
Get detailed merge request information.
```json
{
  "project_id": "group/project",
  "mr_iid": 456
}
```

#### `gitlab_update_merge_request`
Update merge request fields.
```json
{
  "project_id": "group/project",
  "mr_iid": 456,
  "title": "Updated title",
  "description": "New description",
  "labels": "bug,priority"
}
```

#### `gitlab_merge_merge_request`
Merge a merge request with options.
```json
{
  "project_id": "group/project",
  "mr_iid": 456,
  "squash": true,
  "should_remove_source_branch": true
}
```

#### `gitlab_approve_merge_request`
Approve a merge request.
```json
{
  "project_id": "group/project",
  "mr_iid": 456
}
```

### Repository Operations

#### `gitlab_get_file_content`
Read file content from the repository.
```json
{
  "project_id": "group/project",
  "file_path": "src/main.py",
  "ref": "main"
}
```

#### `gitlab_create_commit`
Create a commit with multiple file changes.
```json
{
  "project_id": "group/project",
  "branch": "feature-branch",
  "commit_message": "Add new features",
  "actions": [
    {
      "action": "create",
      "file_path": "new_file.py",
      "content": "print('Hello')"
    },
    {
      "action": "update",
      "file_path": "existing.py",
      "content": "# Updated content"
    }
  ]
}
```

#### `gitlab_compare_refs`
Compare two branches, tags, or commits.
```json
{
  "project_id": "group/project",
  "from_ref": "main",
  "to_ref": "feature-branch"
}
```

### CI/CD Jobs and Artifacts

#### `gitlab_list_pipeline_jobs`
List jobs in a specific CI/CD pipeline.
```json
{
  "project_id": "group/project",
  "pipeline_id": 789,
  "per_page": 20,
  "page": 1
}
```

#### `gitlab_list_project_jobs`
List jobs for a project with optional scope filtering.
```json
{
  "project_id": "group/project",
  "scope": "failed",
  "per_page": 25
}
```

#### `gitlab_download_job_artifact`
Get information about job artifacts (security note: content not downloaded).
```json
{
  "project_id": "group/project",
  "job_id": 456,
  "artifact_path": "build.zip"
}
```

### Advanced Tools

#### `gitlab_batch_operations`
Execute multiple operations atomically with rollback support.
```json
{
  "project_id": "group/project",
  "operations": [
    {
      "name": "get_issue",
      "tool": "gitlab_get_issue",
      "arguments": {"issue_iid": 123}
    },
    {
      "name": "create_mr",
      "tool": "gitlab_create_merge_request",
      "arguments": {
        "source_branch": "fix-{{get_issue.iid}}",
        "target_branch": "main",
        "title": "Fix: {{get_issue.title}}"
      }
    }
  ]
}
```

#### `gitlab_summarize_merge_request`
Generate an AI-friendly summary of a merge request.
```json
{
  "project_id": "group/project",
  "mr_iid": 456,
  "max_length": 500
}
```

#### `gitlab_smart_diff`
Get a structured diff with context and size limits.
```json
{
  "project_id": "group/project",
  "from_ref": "main",
  "to_ref": "feature",
  "context_lines": 3,
  "max_file_size": 50000
}
```

### User & Profile Management

#### `gitlab_search_user`
Search for GitLab users by name, username, or email.
```json
{
  "search": "John",
  "per_page": 10
}
```

#### `gitlab_get_user_details`  
Get comprehensive user profile and metadata.
```json
{
  "username": "johndoe"
}
```

#### `gitlab_get_my_profile`
Get the current authenticated user's complete profile.
```json
{}
```

#### `gitlab_get_user_contributions_summary`
Summarize user's recent contributions across issues, MRs, and commits.
```json
{
  "username": "johndoe",
  "since": "2024-01-01",
  "until": "2024-01-31"
}
```

#### `gitlab_get_user_activity_feed`
Retrieve user's complete activity/events timeline.
```json
{
  "username": "johndoe", 
  "target_type": "Issue",
  "after": "2024-01-01"
}
```

### User's Issues & Merge Requests

#### `gitlab_get_user_open_mrs`
Get all open merge requests authored by a user.
```json
{
  "username": "johndoe",
  "sort": "updated"
}
```

#### `gitlab_get_user_review_requests`
Get MRs where user is assigned as reviewer with pending action.
```json
{
  "username": "johndoe",
  "priority": "high",
  "sort": "urgency"
}
```

#### `gitlab_get_user_open_issues`
Get open issues assigned to a user, prioritized by severity/SLA.
```json
{
  "username": "johndoe",
  "sla_status": "overdue",
  "sort": "priority"
}
```

#### `gitlab_get_user_reported_issues`
Get issues reported/created by a user.
```json
{
  "username": "johndoe",
  "state": "opened",
  "since": "2024-01-01"
}
```

#### `gitlab_get_user_resolved_issues`
Get issues closed/resolved by a user.
```json
{
  "username": "johndoe",
  "since": "2024-01-01",
  "until": "2024-03-31"
}
```

### User's Code & Commits

#### `gitlab_get_user_commits`
Get commits authored by a user within date range or branch.
```json
{
  "username": "johndoe", 
  "branch": "main",
  "since": "2024-01-01",
  "include_stats": true
}
```

### Complete Tool List

- **Projects**: `gitlab_list_projects`, `gitlab_get_project`, `gitlab_get_current_project`, `gitlab_search_projects`
- **Issues**: `gitlab_list_issues`, `gitlab_get_issue`, `gitlab_add_issue_comment`, `gitlab_summarize_issue`
- **Merge Requests**: `gitlab_list_merge_requests`, `gitlab_get_merge_request`, `gitlab_update_merge_request`, `gitlab_close_merge_request`, `gitlab_merge_merge_request`, `gitlab_add_merge_request_comment`, `gitlab_get_merge_request_notes`, `gitlab_approve_merge_request`, `gitlab_get_merge_request_approvals`, `gitlab_get_merge_request_discussions`, `gitlab_resolve_discussion`, `gitlab_get_merge_request_changes`, `gitlab_rebase_merge_request`
- **Repository**: `gitlab_get_file_content`, `gitlab_list_repository_tree`, `gitlab_list_commits`, `gitlab_get_commit`, `gitlab_get_commit_diff`, `gitlab_create_commit`, `gitlab_cherry_pick_commit`, `gitlab_compare_refs`, `gitlab_list_tags`
- **Branches**: `gitlab_list_branches`
- **Pipelines & Jobs**: `gitlab_list_pipelines`, `gitlab_list_pipeline_jobs`, `gitlab_list_project_jobs`, `gitlab_download_job_artifact`, `gitlab_summarize_pipeline`
- **Search**: `gitlab_search_projects`, `gitlab_search_in_project`
- **Users**: `gitlab_get_current_user`, `gitlab_get_user`, `gitlab_list_user_events`, `gitlab_list_project_members`
- **User & Profile**: `gitlab_search_user`, `gitlab_get_user_details`, `gitlab_get_my_profile`, `gitlab_get_user_contributions_summary`, `gitlab_get_user_activity_feed`
- **User's Issues & MRs**: `gitlab_get_user_open_mrs`, `gitlab_get_user_review_requests`, `gitlab_get_user_open_issues`, `gitlab_get_user_reported_issues`, `gitlab_get_user_resolved_issues`
- **User's Code & Commits**: `gitlab_get_user_commits`
- **Releases**: `gitlab_list_releases`
- **Webhooks**: `gitlab_list_project_hooks`
- **AI Tools**: `gitlab_summarize_merge_request`, `gitlab_summarize_issue`, `gitlab_summarize_pipeline`
- **Advanced**: `gitlab_batch_operations`, `gitlab_smart_diff`, `gitlab_safe_preview_commit`

## Examples

### Auto-detect and List Issues
```python
# First get current project from git repo
project = await session.call_tool("gitlab_get_current_project")

# Then list open issues
issues = await session.call_tool("gitlab_list_issues", {
    "state": "opened"
})
```

### Create a Fix with Batch Operations
```python
# Atomically: get issue → create branch → commit fix → create MR
result = await session.call_tool("gitlab_batch_operations", {
    "operations": [
        {
            "name": "issue",
            "tool": "gitlab_get_issue", 
            "arguments": {"issue_iid": 123}
        },
        {
            "name": "fix",
            "tool": "gitlab_create_commit",
            "arguments": {
                "branch": "fix-issue-{{issue.iid}}",
                "commit_message": "Fix: {{issue.title}}",
                "actions": [{
                    "action": "update",
                    "file_path": "src/bug.py",
                    "content": "# Fixed code here"
                }]
            }
        },
        {
            "name": "mr",
            "tool": "gitlab_create_merge_request",
            "arguments": {
                "source_branch": "fix-issue-{{issue.iid}}",
                "target_branch": "main",
                "title": "Fix: {{issue.title}}",
                "description": "Fixes #{{issue.iid}}"
            }
        }
    ]
})
```

## Development

### Quick Start

```bash
# Install development dependencies
make install-dev

# Run all checks locally
make ci-local

# Format code
make format

# Run tests with coverage
make test-cov
```

### CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

- **CI Pipeline**: Runs on every push and PR
  - Linting (Ruff, Black, isort, MyPy)
  - Testing (pytest with coverage)
  - Security scanning (Bandit, Safety, pip-audit)
  - Multi-version Python testing (3.10, 3.11, 3.12)
  
- **Code Quality**: 
  - SonarCloud analysis
  - CodeQL security analysis
  - Complexity metrics (Radon, Xenon)
  
- **Release Pipeline**: Automated releases on version tags
  - PyPI package publishing
  - Docker image building and publishing
  - GitHub release creation

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=mcp_gitlab

# Run specific test file
uv run pytest tests/test_gitlab_client.py -v
```

### Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

```bash
# Format code
black src/ tests/
isort src/ tests/

# Run linters
flake8 src/ tests/
mypy src/
```

## Troubleshooting

### Authentication Issues
- Ensure your token has the required scopes (`api`, `read_repository`, `write_repository`)
- Check token expiration date
- Verify GitLab URL if using self-hosted instance

### Rate Limiting
GitLab API has rate limits. The server handles rate limit errors gracefully and returns appropriate error messages.

### Large Responses
Responses are automatically truncated if they exceed size limits. Use pagination parameters to retrieve data in chunks.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol](https://github.com/anthropics/mcp)
- Uses [python-gitlab](https://github.com/python-gitlab/python-gitlab) for GitLab API interaction
- Inspired by the need for better LLM-GitLab integration