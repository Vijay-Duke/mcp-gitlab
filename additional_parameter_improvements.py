"""
Additional parameter improvements based on Atlassian MCP tool review recommendations.
These address specific GitLab API parameters that need better examples and guidance.
"""

# Based on Atlassian review recommendations for complex parameters
ADDITIONAL_PARAMETER_IMPROVEMENTS = {
    
    # For issue and MR creation tools
    "custom_attributes": {
        "description": """Custom attributes for GitLab objects (JSON object).
        
The keys are custom attribute keys and values are the data to set.
**Example: `{"priority": "high", "team": "backend", "environment": "production"}`**

Common use cases:
- Project categorization: {"department": "engineering", "cost_center": "R&D"}
- Issue tracking: {"severity": "critical", "customer": "enterprise_client", "component": "auth"}
- User metadata: {"role": "tech_lead", "location": "remote", "timezone": "UTC-8"}
- Environment tags: {"env": "production", "region": "us-west", "cluster": "k8s-prod"}

Note: Custom attributes must be enabled at the project or group level.""",
    },
    
    # Enhanced scope parameter for search operations
    "search_scope": {
        "description": """Search scope to limit results (string).

**Examples for different search contexts:**
- Code search: `"blobs"` (search in file contents)
- Issue search: `"issues"` (search in issues only)  
- Commit search: `"commits"` (search commit messages and diffs)
- Wiki search: `"wiki_blobs"` (search wiki pages)
- Milestone search: `"milestones"` (search milestone titles/descriptions)

**Example combinations:**
- Find security issues: scope="issues", search="security vulnerability"
- Find authentication code: scope="blobs", search="function authenticate" 
- Find bug fix commits: scope="commits", search="fix bug memory leak"

Available scopes depend on the tool - check tool description for valid options.""",
    },
    
    # Enhanced merge request options
    "merge_options": {
        "description": """Merge options configuration (JSON object).

**Example: `{"squash": true, "delete_source_branch": true, "merge_when_pipeline_succeeds": true}`**

Available options:
- `squash`: true/false - Squash commits when merging
- `delete_source_branch`: true/false - Delete source branch after merge  
- `merge_when_pipeline_succeeds`: true/false - Auto-merge when CI passes
- `should_remove_source_branch`: true/false - Remove source branch (deprecated, use delete_source_branch)

**Common patterns:**
- Clean merge: `{"squash": true, "delete_source_branch": true}`
- Safe merge: `{"merge_when_pipeline_succeeds": true}`
- Feature branch: `{"squash": false, "delete_source_branch": false}`""",
    },
    
    # File operations for commits
    "file_actions": {
        "description": """File operations for commit creation (array of objects).

Each action object specifies a file operation to perform in the commit.

**Example for multiple operations:**
```json
[
  {
    "action": "create",
    "file_path": "src/new_feature.py", 
    "content": "def new_function():\\n    return 'Hello'"
  },
  {
    "action": "update",
    "file_path": "README.md",
    "content": "Updated documentation"
  },
  {
    "action": "delete",
    "file_path": "deprecated/old_file.py"
  }
]
```

**Available actions:**
- `create`: Create new file (content required)
- `update`: Modify existing file (content required)
- `delete`: Remove file (content not needed)
- `move`: Rename/move file (previous_path required)

**Action-specific fields:**
- All actions: `action`, `file_path` 
- create/update: `content` (file contents as string)
- move: `previous_path` (original file path)""",
    },
    
    # Pipeline configuration
    "pipeline_variables": {
        "description": """Pipeline variables to pass to CI/CD (JSON object).

Variables are passed as environment variables to pipeline jobs.

**Example: `{"ENVIRONMENT": "staging", "DEPLOY_TARGET": "k8s-staging", "DEBUG": "true"}`**

**Common use cases:**
- Environment control: `{"ENVIRONMENT": "production", "REGION": "us-east-1"}`
- Feature flags: `{"FEATURE_X_ENABLED": "true", "EXPERIMENTAL_MODE": "false"}`
- Deployment config: `{"DEPLOY_TARGET": "staging", "REPLICAS": "3"}`
- Debug options: `{"DEBUG": "true", "VERBOSE": "1", "LOG_LEVEL": "debug"}`

**Best practices:**
- Use uppercase for environment variables
- String values only (numbers as strings: "123" not 123)
- Boolean as strings: "true"/"false"
- Sensitive values should use CI/CD variables, not pipeline variables""",
    },
    
    # Advanced filtering for lists
    "advanced_filters": {
        "description": """Advanced filtering options (JSON object).

**Example: `{"state": "opened", "labels": ["bug", "high-priority"], "created_after": "2024-01-01"}`**

**Common filter combinations:**

For issues:
```json
{
  "state": "opened",
  "labels": ["bug", "critical"],
  "assignee_id": 123,
  "created_after": "2024-01-01",
  "milestone": "v2.0"
}
```

For merge requests:
```json
{
  "state": "opened", 
  "target_branch": "main",
  "author_id": 456,
  "updated_after": "2024-01-01",
  "wip": "no"
}
```

**Date formats:** Use ISO 8601 format: "2024-01-01" or "2024-01-01T10:30:00Z"
**Arrays:** Use arrays for multiple values: `["bug", "feature"]`
**Booleans:** Use strings: `"yes"/"no"` not `true/false`""",
    },
}

# Integration examples showing how these work together
INTEGRATION_EXAMPLES = {
    "create_comprehensive_issue": """
    Create an issue with all advanced options:
    ```json
    {
      "title": "Critical authentication bug in production",
      "description": "Users cannot login after latest deployment",
      "labels": ["bug", "critical", "security"],
      "assignee_ids": [123, 456],
      "milestone_id": 42,
      "custom_attributes": {
        "severity": "critical",
        "component": "authentication", 
        "customer_impact": "high",
        "environment": "production"
      }
    }
    ```
    """,
    
    "advanced_merge_request": """
    Create MR with pipeline variables and merge options:
    ```json
    {
      "title": "Feature: Add OAuth integration",
      "source_branch": "feature/oauth-integration",
      "target_branch": "main",
      "description": "Implements OAuth 2.0 authentication",
      "labels": ["feature", "security"],
      "assignee_ids": [789],
      "merge_options": {
        "squash": true,
        "delete_source_branch": true,
        "merge_when_pipeline_succeeds": true
      },
      "pipeline_variables": {
        "RUN_SECURITY_SCAN": "true",
        "DEPLOY_TO_STAGING": "true",
        "NOTIFY_TEAM": "security"
      }
    }
    ```
    """,
    
    "bulk_file_commit": """
    Create commit with multiple file operations:
    ```json
    {
      "branch": "feature/refactor-auth",
      "commit_message": "Refactor authentication system",
      "file_actions": [
        {
          "action": "create",
          "file_path": "src/auth/oauth.py",
          "content": "class OAuthProvider:\\n    def authenticate(self, token):\\n        pass"
        },
        {
          "action": "update", 
          "file_path": "src/auth/__init__.py",
          "content": "from .oauth import OAuthProvider\\nfrom .basic import BasicAuth"
        },
        {
          "action": "delete",
          "file_path": "src/auth/deprecated_auth.py"
        },
        {
          "action": "move",
          "file_path": "src/auth/basic_auth.py",
          "previous_path": "src/auth/basic.py"
        }
      ]
    }
    ```
    """
}

print("Additional parameter improvements ready for integration into tool descriptions")
print("These follow Atlassian MCP review patterns for complex parameter documentation")