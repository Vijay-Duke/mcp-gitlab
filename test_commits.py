#!/usr/bin/env python3
"""Test script for GitLab commits functionality"""

import os
from mcp_gitlab.gitlab_client import GitLabClient, GitLabConfig

# Setup configuration
config = GitLabConfig(
    url=os.getenv("GITLAB_URL", "https://gitlab.com"),
    private_token=os.getenv("GITLAB_TOKEN")
)

# Create client
client = GitLabClient(config)

# Test with the project ID from the error
project_id = "48563418"
ref_name = "master"
per_page = 3

print(f"Testing get_commits for project {project_id}...")
print(f"Parameters: ref_name={ref_name}, per_page={per_page}")

try:
    result = client.get_commits(
        project_id=project_id,
        ref_name=ref_name,
        per_page=per_page
    )
    print("Success!")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()