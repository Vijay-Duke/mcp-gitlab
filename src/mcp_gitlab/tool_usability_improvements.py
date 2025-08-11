"""
Improved tool descriptions for better LLM usability.
Based on Atlassian MCP tool usability review recommendations.

This file contains improved descriptions that make it clearer for LLMs to select 
the correct tool by reducing ambiguity and providing explicit usage guidance.
"""

# ============================================================================
# USER TOOL IMPROVEMENTS
# ============================================================================

# Before: Ambiguous between get_user, search_user, get_user_details
IMPROVED_USER_TOOLS = {
    "gitlab_get_user": {
        "description": """Get basic profile information for a specific GitLab user by ID or username.
        
Returns essential user details like name, username, avatar, and public profile info.
**Use this tool when you have a specific user ID or exact username and need basic profile information.**

Examples:
- Get user profile for @mentions: get_user(username="johndoe")  
- Look up user from commit author: get_user(user_id=12345)
- Display user info in applications

For searching users with partial information, use 'search_users_by_query' instead.
For comprehensive user activity and contributions, use 'get_user_activity_summary' instead."""
    },
    
    "gitlab_search_user": {
        "new_name": "gitlab_search_users_by_query",
        "description": """Search for GitLab users based on partial information or search criteria.

This tool is useful when you don't have the exact username or ID, but need to find users 
based on name, email, or other search terms.
**Use this tool when you need to find users based on partial information or search queries.**

Examples:
- Find users by partial name: search_users_by_query("John Sm")
- Search by email domain: search_users_by_query("@company.com") 
- Find users for team assignments

For getting specific user details when you have exact ID/username, use 'get_user' instead."""
    },
    
    "gitlab_get_user_details": {
        "new_name": "gitlab_get_user_activity_summary", 
        "description": """Get comprehensive activity summary and contributions for a specific user.

Returns detailed information about a user's GitLab activity including recent contributions,
project involvement, and activity statistics.
**Use this tool when you need detailed insights into a user's GitLab activity and contributions.**

Examples:
- Performance reviews: get_user_activity_summary(user_id=123)
- Team member activity overview
- Contributor analysis for projects

For basic user profile info, use 'get_user' instead.
For finding users by search, use 'search_users_by_query' instead."""
    }
}

# ============================================================================
# ACTIVITY VS EVENTS CLARIFICATION  
# ============================================================================

IMPROVED_ACTIVITY_TOOLS = {
    "gitlab_list_user_events": {
        "new_name": "gitlab_list_user_system_events",
        "description": """List recent system events and actions performed by a user.
        
Shows low-level system events like login, project joins, key additions, etc.
**Use this tool when you need system-level audit information or administrative events.**

Examples:
- Security audit: list_user_system_events(user_id=123)
- Account activity monitoring
- Administrative oversight

For user's content activity (commits, issues, MRs), use 'get_user_activity_feed' instead."""
    },
    
    "gitlab_get_user_activity_feed": {
        "description": """Get a user's content activity feed including commits, issues, merge requests, and comments.
        
Shows meaningful development activity and contributions, similar to a GitHub activity feed.
**Use this tool when you want to see what a user has been working on recently.**

Examples:
- Team standup summaries: get_user_activity_feed(user_id=123)
- Recent work overview  
- Development activity tracking

For system-level events (logins, permissions), use 'list_user_system_events' instead."""
    }
}

# ============================================================================
# COMMIT TOOLS CLARIFICATION
# ============================================================================

IMPROVED_COMMIT_TOOLS = {
    "gitlab_get_user_commits": {
        "new_name": "gitlab_list_commits_authored_by_user",
        "description": """List all commits authored by a specific user across projects or within a project.
        
Shows commits where the user is the author (wrote the code).
**Use this tool to see what code changes a user has authored.**

Examples:
- Code contribution analysis: list_commits_authored_by_user(user_id=123)
- Developer productivity metrics
- Code review preparation  

For merge commits specifically, use 'list_merge_commits_by_user' instead."""
    },
    
    "gitlab_get_user_merge_commits": {
        "new_name": "gitlab_list_merge_commits_by_user", 
        "description": """List merge commits where a specific user performed the merge.
        
Shows commits where the user merged branches (not necessarily the code author).
**Use this tool to see what merges a user has performed, useful for release management.**

Examples:
- Release management: list_merge_commits_by_user(user_id=123)
- Merge activity tracking
- Integration oversight

For all commits authored by user, use 'list_commits_authored_by_user' instead."""
    }
}

# ============================================================================
# ISSUE AND MR TOOLS CLARIFICATION
# ============================================================================

IMPROVED_ISSUE_MR_TOOLS = {
    "gitlab_get_user_open_issues": {
        "description": """List open issues assigned to or created by a specific user.
        
**Use this tool to see what issues a user is currently working on or responsible for.**

Examples:
- Sprint planning: get_user_open_issues(user_id=123)
- Workload assessment
- Task assignment review"""
    },
    
    "gitlab_get_user_reported_issues": {
        "new_name": "gitlab_list_issues_created_by_user",
        "description": """List all issues created/reported by a specific user (including closed ones).
        
Shows issues where the user is the original reporter/creator.
**Use this tool to see what problems or requests a user has reported.**

Examples:
- Bug reporting patterns: list_issues_created_by_user(user_id=123)
- User feedback analysis
- Historical issue creation"""
    },
    
    "gitlab_get_user_review_requests": {
        "new_name": "gitlab_list_mrs_awaiting_user_review",
        "description": """List merge requests where a specific user is requested as a reviewer.
        
**Use this tool to see what merge requests need a specific user's review.**

Examples:
- Review queue management: list_mrs_awaiting_user_review(user_id=123)
- Code review assignment tracking
- Team review workload balancing"""
    }
}

# ============================================================================
# PARAMETER IMPROVEMENTS WITH EXAMPLES
# ============================================================================

IMPROVED_PARAMETER_DESCRIPTIONS = {
    "custom_attributes": {
        "description": """Custom attributes for GitLab objects (JSON object).
        
The keys are custom attribute names and values are the data to set.
**Example: `{"environment": "production", "team": "backend", "priority": "high"}`**
        
Common use cases:
- Project categorization: {"department": "engineering", "cost_center": "R&D"}
- Issue tracking: {"severity": "critical", "customer": "enterprise_client"}
- User metadata: {"role": "tech_lead", "location": "remote"}"""
    },
    
    "labels": {
        "description": """Labels to assign (array of strings).
        
**Example: `["bug", "frontend", "high-priority"]`**
        
Best practices:
- Use consistent naming: ["bug", "feature", "docs"] not ["Bug", "FEATURE", "documentation"]
- Category prefixes: ["type:bug", "priority:high", "team:frontend"]
- Environment tags: ["env:prod", "env:staging", "env:dev"]"""
    },
    
    "assignee_ids": {
        "description": """User IDs to assign (array of integers).
        
**Example: `[123, 456, 789]` for multiple assignees**
**Example: `[123]` for single assignee**
        
How to find user IDs:
1. Use search_users_by_query() to find users
2. Get user_id from the response  
3. Use those IDs in this parameter"""
    },
    
    "milestone_id": {
        "description": """Milestone ID to assign (integer).
        
**Example: `42` (milestone ID)**
        
How to find milestone ID:
1. Use list_project_milestones() to see available milestones
2. Get id field from the milestone you want
3. Use that ID here"""
    }
}

# ============================================================================
# SEARCH TOOLS CLARIFICATION
# ============================================================================

IMPROVED_SEARCH_TOOLS = {
    "gitlab_search_projects": {
        "description": """Search for GitLab projects across the entire instance based on name or description.
        
**Use this tool when you need to find projects but don't know their exact names or paths.**

Examples:
- Find projects to contribute to: search_projects("react dashboard")
- Discover similar projects: search_projects("microservice")
- Organization-wide project discovery

For searching within a specific project's content, use 'search_in_project' instead."""
    },
    
    "gitlab_search_in_project": {
        "new_name": "gitlab_search_project_content",
        "description": """Search within a specific project for code, files, commits, issues, or merge requests.
        
**Use this tool when you want to search inside a known project for specific content.**

Examples:
- Find code: search_project_content(project_id=123, scope="blobs", search="function authenticate")
- Find issues: search_project_content(project_id=123, scope="issues", search="bug report")
- Search commits: search_project_content(project_id=123, scope="commits", search="fix memory leak")

For finding projects by name, use 'search_projects' instead."""
    }
}

# Usage guidance for developers applying these improvements
USAGE_GUIDELINES = """
## How to Apply These Improvements

1. **Update tool descriptions**: Replace existing descriptions with the improved ones
2. **Consider renaming tools**: Some tools have suggested new names for clarity
3. **Add usage examples**: Include concrete examples in parameter descriptions
4. **Use explicit guidance**: Add "Use this tool when..." statements
5. **Cross-reference related tools**: Help LLMs understand when NOT to use a tool

## Key Principles from Atlassian Review

- **Reduce ambiguity**: Make it clear when to use each tool
- **Provide examples**: Concrete examples help LLMs understand usage
- **Differentiate similar tools**: Explain the difference explicitly  
- **Add context**: Explain not just what the tool does, but when to use it
- **Include negative guidance**: When NOT to use a tool is as important as when to use it
"""