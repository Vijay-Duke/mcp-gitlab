# GitLab MCP Tool Usability Improvements

This document outlines the usability improvements applied to the GitLab MCP server tools based on the Atlassian MCP tool review recommendations. These changes improve tool clarity and make it easier for Large Language Models (LLMs) to select the correct tool for a given task.

## 🎯 Key Objectives

1. **Reduce Ambiguity**: Make it clear when to use each tool
2. **Provide Examples**: Include concrete usage examples
3. **Differentiate Similar Tools**: Explain differences explicitly  
4. **Add Contextual Guidance**: Help LLMs understand when NOT to use a tool
5. **Improve Parameter Clarity**: Add examples for complex parameters

## 🔧 Applied Improvements

### 1. User Tool Disambiguation

**Problem**: Confusion between `gitlab_get_user`, `gitlab_search_user`, and `gitlab_get_user_details`

**Solution**: Clear usage guidance and explicit differentiation

#### Before vs After:

**gitlab_get_user** (Updated):
```
Get basic profile information for a specific GitLab user by ID or username.

**Use this tool when you have a specific user ID or exact username and need basic profile information.**

Examples:
- Get user profile for @mentions: get_user(username="johndoe")  
- Look up user from commit author: get_user(user_id=12345)

For searching users with partial information, use 'gitlab_search_user' instead.
```

**gitlab_search_user** (Improved):
```  
Search for GitLab users based on partial information or search criteria.

**Use this tool when you need to find users based on partial information or search queries.**

Examples:
- Find users by partial name: search_user("John Sm")
- Search by email domain: search_user("@company.com")

For getting specific user details when you have exact ID/username, use 'gitlab_get_user' instead.
```

**gitlab_get_user_details** (Renamed & Clarified):
```
Get comprehensive activity summary and contributions for a specific user.

**Use this tool when you need detailed insights into a user's GitLab activity and contributions.**

Examples:
- Performance reviews: get_user_details(user_id=123)
- Team member activity overview

For basic user profile info, use 'gitlab_get_user' instead.
```

### 2. Activity vs Events Clarification

**Problem**: Ambiguity between `gitlab_list_user_events` and `gitlab_get_user_activity_feed`

**Recommended Solution** (for future implementation):

**gitlab_list_user_events** → **gitlab_list_user_system_events**:
```
List recent system events and actions performed by a user.

**Use this tool when you need system-level audit information or administrative events.**

Examples:
- Security audit: list_user_system_events(user_id=123)
- Account activity monitoring

For user's content activity (commits, issues, MRs), use 'get_user_activity_feed' instead.
```

**gitlab_get_user_activity_feed** (Clarified):
```
Get a user's content activity feed including commits, issues, merge requests, and comments.

**Use this tool when you want to see what a user has been working on recently.**

Examples:
- Team standup summaries: get_user_activity_feed(user_id=123)
- Development activity tracking

For system-level events (logins, permissions), use 'list_user_system_events' instead.
```

### 3. Commit Tool Differentiation

**Problem**: Similar functionality between `gitlab_get_user_commits` and `gitlab_get_user_merge_commits`

**Recommended Solution**:

**gitlab_get_user_commits** → **gitlab_list_commits_authored_by_user**:
```
List all commits authored by a specific user across projects or within a project.

**Use this tool to see what code changes a user has authored.**

Examples:
- Code contribution analysis: list_commits_authored_by_user(user_id=123)
- Developer productivity metrics

For merge commits specifically, use 'list_merge_commits_by_user' instead.
```

**gitlab_get_user_merge_commits** → **gitlab_list_merge_commits_by_user**:
```
List merge commits where a specific user performed the merge.

**Use this tool to see what merges a user has performed, useful for release management.**

Examples:
- Release management: list_merge_commits_by_user(user_id=123)
- Integration oversight

For all commits authored by user, use 'list_commits_authored_by_user' instead.
```

### 4. Enhanced Parameter Descriptions

**Problem**: Complex parameters without examples or usage guidance

**Solution**: Added concrete examples and best practices

#### Improved Parameters:

**labels**:
```
Labels to assign (array of strings).

**Example: `["bug", "frontend", "high-priority"]`**

Best practices:
- Use consistent naming: ["bug", "feature", "docs"] not ["Bug", "FEATURE", "documentation"]
- Category prefixes: ["type:bug", "priority:high", "team:frontend"]
- Environment tags: ["env:prod", "env:staging", "env:dev"]
```

**assignee_ids**:
```
User IDs to assign (array of integers).

**Example: `[123, 456, 789]` for multiple assignees**
**Example: `[123]` for single assignee**

How to find user IDs:
1. Use gitlab_search_user() to find users
2. Get user_id from the response  
3. Use those IDs in this parameter
```

**milestone_id**:
```
Milestone ID to assign (integer).

**Example: `42` (milestone ID)**

How to find milestone ID:
1. Use gitlab_list_project_milestones() to see available milestones
2. Get id field from the milestone you want
3. Use that ID here
```

**custom_attributes**:
```
Custom attributes for GitLab objects (JSON object).

**Example: `{"environment": "production", "team": "backend", "priority": "high"}`**

Common use cases:
- Project categorization: {"department": "engineering", "cost_center": "R&D"}
- Issue tracking: {"severity": "critical", "customer": "enterprise_client"}
```

### 5. Search Tool Clarification

**Problem**: Confusion between `gitlab_search_projects` and `gitlab_search_in_project`

**Recommended Solution**:

**gitlab_search_projects** (Clarified):
```
Search for GitLab projects across the entire instance based on name or description.

**Use this tool when you need to find projects but don't know their exact names or paths.**

Examples:
- Find projects to contribute to: search_projects("react dashboard")
- Organization-wide project discovery

For searching within a specific project's content, use 'search_in_project' instead.
```

**gitlab_search_in_project** → **gitlab_search_project_content**:
```
Search within a specific project for code, files, commits, issues, or merge requests.

**Use this tool when you want to search inside a known project for specific content.**

Examples:
- Find code: search_project_content(project_id=123, scope="blobs", search="function authenticate")
- Find issues: search_project_content(project_id=123, scope="issues", search="bug report")

For finding projects by name, use 'search_projects' instead.
```

## 📋 Implementation Status

### ✅ Completed Improvements

1. **User Tool Descriptions**: Updated `gitlab_get_user`, `gitlab_search_user`, and `gitlab_get_user_details`
2. **Parameter Examples**: Created comprehensive examples for complex parameters
3. **Usage Guidance**: Added "Use this tool when..." statements
4. **Cross-References**: Added "For X instead, use Y tool" guidance
5. **Documentation**: Created comprehensive improvement guides

### 🔄 Recommended for Future Implementation

1. **Tool Renaming**: Consider renaming tools for better clarity
   - `gitlab_get_user_details` → `gitlab_get_user_activity_summary`
   - `gitlab_list_user_events` → `gitlab_list_user_system_events`
   - `gitlab_search_in_project` → `gitlab_search_project_content`

2. **Additional Parameter Examples**: Apply improved parameter descriptions to all tools

3. **Issue/MR Tool Clarification**: 
   - `gitlab_get_user_reported_issues` → `gitlab_list_issues_created_by_user`
   - `gitlab_get_user_review_requests` → `gitlab_list_mrs_awaiting_user_review`

## 🎯 Impact Assessment

### Expected Benefits:

1. **Improved Tool Selection**: LLMs will make better choices between similar tools
2. **Reduced Ambiguity**: Clear guidance on when to use each tool
3. **Better Parameter Usage**: Concrete examples reduce parameter confusion
4. **Enhanced User Experience**: More intuitive tool names and descriptions
5. **Fewer Errors**: Explicit guidance prevents common usage mistakes

### Backward Compatibility:

- All improvements maintain existing tool names and parameters
- Descriptions are enhanced without breaking existing functionality
- Optional renaming suggestions preserve original tool names as aliases

## 🔍 Usage Guidelines for Developers

### When Updating Tool Descriptions:

1. **Add explicit usage guidance**: "Use this tool when..."
2. **Include concrete examples**: Show real parameter values
3. **Cross-reference related tools**: Help users choose correctly
4. **Provide negative guidance**: When NOT to use a tool
5. **Use consistent formatting**: Follow established patterns

### Example Template:

```
DESC_TOOL_NAME = """Brief description of what the tool does.

**Use this tool when you [specific use case guidance].**

Examples:
- [Concrete example 1]: tool_name(param="example")
- [Concrete example 2]: tool_name(param=123)

Returns information including:
- [What the tool returns]

For [alternative use case], use '[alternative_tool]' instead.
"""
```

## 📚 Related Files

- `src/mcp_gitlab/tool_descriptions.py` - Updated tool descriptions
- `src/mcp_gitlab/tool_usability_improvements.py` - Comprehensive improvement plans
- `improved_parameters.py` - Enhanced parameter descriptions with examples
- `examples/handler_example.py` - Implementation examples

## 🚀 Future Enhancements

Based on the Atlassian review, potential future improvements:

1. **Schema Validation**: Add runtime validation for complex parameters
2. **Tool Categorization**: Group related tools in the UI/documentation
3. **Usage Analytics**: Track which tools are confused and need clarification
4. **Interactive Examples**: Provide runnable examples for complex operations
5. **Context-Aware Suggestions**: Suggest related tools based on current usage

---

*These usability improvements make the GitLab MCP server more intuitive and reduce ambiguity for both human users and LLM agents.*