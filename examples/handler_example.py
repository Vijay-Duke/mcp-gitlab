"""Example of how to use the new decorators and validation utilities.

This demonstrates refactoring a tool handler to use our new helper decorators
and validation utilities to reduce boilerplate and improve error handling.
"""

from mcp import types

from mcp_gitlab.decorators import gitlab_tool, format_response
from mcp_gitlab.validation import validate_tool_args
from mcp_gitlab.gitlab_client import GitLabClient


# Before: Traditional handler with lots of boilerplate
async def list_projects_old(client: GitLabClient, request: types.CallToolRequest) -> types.CallToolResult:
    """Old style handler with boilerplate."""
    try:
        arguments = request.params.arguments or {}
        
        # Manual authentication check
        if not client.is_authenticated():
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text="GitLab authentication required. Please configure your GitLab token."
                    )
                ]
            )
        
        # Manual pagination validation
        page = arguments.get('page', 1)
        per_page = arguments.get('per_page', 20)
        
        if not isinstance(page, int) or page < 1:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text="Page must be a positive integer"
                    )
                ]
            )
        
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text="Per page must be an integer between 1 and 100"
                    )
                ]
            )
        
        # Manual GitLab API call with error handling
        try:
            projects = client.gl.projects.list(page=page, per_page=per_page, all=False)
            
            # Manual response formatting
            if not projects:
                text = "No projects found."
            else:
                lines = []
                for project in projects:
                    lines.append(f"ID: {project.id}, Name: {project.name}, Path: {project.path_with_namespace}")
                text = "\n".join(lines)
            
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=text
                    )
                ]
            )
            
        except Exception as e:
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"GitLab API error: {str(e)}"
                    )
                ]
            )
            
    except Exception as e:
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"An unexpected error occurred: {str(e)}"
                )
            ]
        )


# After: Clean handler using decorators
@gitlab_tool(requires_auth=True, paginated=True, max_per_page=100)
@validate_tool_args(
    optional_args={
        'page': int,
        'per_page': int,
        'search': str,
        'visibility': str
    }
)
async def list_projects_new(client: GitLabClient, request: types.CallToolRequest) -> types.CallToolResult:
    """New style handler with decorators - much cleaner!"""
    arguments = request.params.arguments or {}
    
    # Extract parameters (validation already done by decorators)
    page = arguments.get('page', 1)
    per_page = arguments.get('per_page', 20)
    search = arguments.get('search')
    visibility = arguments.get('visibility')
    
    # Build query parameters
    query_params = {
        'page': page,
        'per_page': per_page,
        'all': False
    }
    
    if search:
        query_params['search'] = search
    if visibility:
        query_params['visibility'] = visibility
    
    # Make API call (error handling done by decorator)
    projects = client.gl.projects.list(**query_params)
    
    # Format response data
    project_data = []
    for project in projects:
        project_data.append({
            'id': project.id,
            'name': project.name,
            'path': project.path_with_namespace,
            'description': getattr(project, 'description', ''),
            'visibility': getattr(project, 'visibility', ''),
            'last_activity': getattr(project, 'last_activity_at', ''),
            'web_url': getattr(project, 'web_url', '')
        })
    
    # Use helper to format response consistently
    return format_response(
        project_data,
        template="Found {data_len} projects:\n\n{formatted_data}"
    )


# Example of a more complex handler with custom validation
@gitlab_tool(requires_auth=True, paginated=False)
@validate_tool_args(
    required_args={
        'project_id': (str, int),
        'title': str
    },
    optional_args={
        'description': str,
        'assignee_id': int,
        'labels': list,
        'milestone_id': int
    }
)
async def create_issue_example(client: GitLabClient, request: types.CallToolRequest) -> types.CallToolResult:
    """Example of creating an issue with validation."""
    arguments = request.params.arguments or {}
    
    # Get project
    project = client.gl.projects.get(arguments['project_id'])
    
    # Build issue data
    issue_data = {
        'title': arguments['title']
    }
    
    # Add optional fields
    if 'description' in arguments:
        issue_data['description'] = arguments['description']
    if 'assignee_id' in arguments:
        issue_data['assignee_id'] = arguments['assignee_id']
    if 'labels' in arguments:
        issue_data['labels'] = arguments['labels']
    if 'milestone_id' in arguments:
        issue_data['milestone_id'] = arguments['milestone_id']
    
    # Create issue
    issue = project.issues.create(issue_data)
    
    # Return formatted response
    return format_response({
        'id': issue.id,
        'iid': issue.iid,
        'title': issue.title,
        'state': issue.state,
        'web_url': issue.web_url,
        'created_at': issue.created_at
    })


if __name__ == "__main__":
    print("This is an example file showing how to use the new decorators.")
    print("Key improvements:")
    print("1. @gitlab_tool handles auth, pagination, and common error cases")
    print("2. @validate_tool_args ensures type safety")
    print("3. format_response() provides consistent formatting")
    print("4. Much less boilerplate code!")
    print("5. Better separation of concerns")
    print("6. More maintainable and testable code")