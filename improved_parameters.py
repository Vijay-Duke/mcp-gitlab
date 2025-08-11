"""
Improved parameter descriptions with examples for better LLM understanding.
These can be added to existing tool descriptions.
"""

IMPROVED_PARAMETERS = {
    "labels": """Labels to assign (array of strings).

**Example: `["bug", "frontend", "high-priority"]`**

Best practices:
- Use consistent naming: ["bug", "feature", "docs"] not ["Bug", "FEATURE", "documentation"]
- Category prefixes: ["type:bug", "priority:high", "team:frontend"]
- Environment tags: ["env:prod", "env:staging", "env:dev"]""",

    "assignee_ids": """User IDs to assign (array of integers).

**Example: `[123, 456, 789]` for multiple assignees**
**Example: `[123]` for single assignee**

How to find user IDs:
1. Use gitlab_search_user() to find users
2. Get user_id from the response  
3. Use those IDs in this parameter""",

    "milestone_id": """Milestone ID to assign (integer).

**Example: `42` (milestone ID)**

How to find milestone ID:
1. Use gitlab_list_project_milestones() to see available milestones
2. Get id field from the milestone you want
3. Use that ID here""",

    "custom_attributes": """Custom attributes for GitLab objects (JSON object).

The keys are custom attribute names and values are the data to set.
**Example: `{"environment": "production", "team": "backend", "priority": "high"}`**

Common use cases:
- Project categorization: {"department": "engineering", "cost_center": "R&D"}
- Issue tracking: {"severity": "critical", "customer": "enterprise_client"}
- User metadata: {"role": "tech_lead", "location": "remote"}""",

    "merge_request_iid": """Internal ID of the merge request within the project (integer).

**Example: `42` (the !42 merge request in the project)**

Note: This is different from the global MR ID. Use the number that appears after ! in GitLab URLs.
- GitLab URL: /project/merge_requests/42 → iid = 42
- Not the same as the global database ID""",

    "issue_iid": """Internal ID of the issue within the project (integer).

**Example: `123` (the #123 issue in the project)**

Note: This is the number that appears after # in GitLab URLs and discussions.
- GitLab URL: /project/issues/123 → iid = 123
- Use this for referencing issues in commits and discussions""",

    "scope": """Search scope to limit results (string).

**Examples for different contexts:**
- Code search: `"blobs"` (search in file contents)
- Issue search: `"issues"` (search in issues only)  
- Commit search: `"commits"` (search commit messages)
- Wiki search: `"wiki_blobs"` (search wiki pages)

Available scopes depend on the tool - check tool description for valid options.""",

    "state": """Filter by item state (string).

**Common values:**
- Issues: `"opened"`, `"closed"`, `"all"`  
- Merge Requests: `"opened"`, `"closed"`, `"merged"`, `"all"`
- Pipelines: `"running"`, `"pending"`, `"success"`, `"failed"`, `"canceled"`

**Example: `"opened"` to see only active items**""",

    "sort": """Sort order for results (string).

**Common sort options:**
- `"created_at"` - Sort by creation date (newest first)
- `"updated_at"` - Sort by last update (most recently updated first)  
- `"title"` - Sort alphabetically by title
- `"priority"` - Sort by priority (highest first)

**Example: `"updated_at"` to see most recently active items first**""",

    "target_branch": """Target branch for merge request (string).

**Example: `"main"` or `"develop"`**

This is the branch that changes will be merged INTO.
- Source branch: where changes come from
- Target branch: where changes go to (this parameter)

Common target branches: "main", "master", "develop", "staging""",

    "source_branch": """Source branch containing the changes (string).

**Example: `"feature/new-dashboard"` or `"bugfix/memory-leak"`**

This is the branch with your changes that you want to merge.
Best practices:
- Use descriptive names: "feature/user-authentication"
- Include type prefix: "bugfix/", "feature/", "hotfix/"
- Keep names concise but clear"""
}

print("These improved parameter descriptions can be integrated into tool_descriptions.py")
print("They provide concrete examples and usage guidance for better LLM understanding.")