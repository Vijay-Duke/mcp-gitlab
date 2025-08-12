#!/usr/bin/env python3
"""Test GitLab connection and smart_diff functionality"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import gitlab
import json

# Load environment variables
load_dotenv()

def test_connection():
    """Test basic GitLab connection"""
    print("Testing GitLab connection...")
    
    # Get credentials
    gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
    private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    
    if not private_token:
        print("ERROR: GITLAB_PRIVATE_TOKEN not found in environment")
        return False
    
    print(f"URL: {gitlab_url}")
    print(f"Token: {private_token[:10]}..." if private_token else "No token")
    
    try:
        # Create GitLab connection
        gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        
        # Test authentication
        print("\nAuthenticating...")
        gl.auth()
        
        # Get current user info
        try:
            current_user = gl.user
            print(f"✓ Authenticated successfully!")
        except:
            # Just confirm auth worked
            print(f"✓ Authentication successful!")
        
        # List projects
        print("\nFetching projects...")
        projects = gl.projects.list(owned=True, per_page=5)
        print(f"✓ Found {len(projects)} projects")
        
        for p in projects[:3]:
            print(f"  - {p.path_with_namespace}")
        
        return True
        
    except gitlab.exceptions.GitlabAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_smart_diff():
    """Test the smart_diff functionality"""
    print("\n\nTesting smart_diff functionality...")
    
    # Get credentials
    gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
    private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    
    if not private_token:
        print("ERROR: GITLAB_PRIVATE_TOKEN not found")
        return False
    
    try:
        gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        gl.auth()
        
        # You'll need to replace this with an actual project ID or path
        # For testing, let's try to find a project automatically
        projects = gl.projects.list(owned=True, per_page=1)
        if not projects:
            print("No projects found to test with")
            return False
        
        project = projects[0]
        print(f"Using project: {project.path_with_namespace}")
        
        # Get branches
        branches = project.branches.list(per_page=2)
        if len(branches) < 1:
            print("Not enough branches to test diff")
            return False
        
        # Try to compare with main/master
        from_ref = "master"  # or "main"
        to_ref = "feature/PLN1-804-Uplift-getServiceActions-api"
        
        print(f"\nTesting comparison: {from_ref} -> {to_ref}")
        
        try:
            # Test the comparison
            comparison = project.repository_compare(from_ref, to_ref)
            
            print(f"✓ Comparison successful!")
            print(f"  - Commits: {len(comparison.get('commits', []))}")
            print(f"  - Diffs: {len(comparison.get('diffs', []))}")
            
            # Show first few diffs
            for diff in comparison.get('diffs', [])[:3]:
                print(f"  - {diff.get('new_path', diff.get('old_path'))}")
            
            return True
            
        except gitlab.exceptions.GitlabGetError as e:
            print(f"✗ Comparison failed: {e}")
            print(f"  Make sure both refs exist: {from_ref} and {to_ref}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("GitLab MCP Connection Test")
    print("=" * 60)
    
    # Test basic connection
    if not test_connection():
        print("\n❌ Basic connection test failed")
        sys.exit(1)
    
    # Test smart_diff
    if not test_smart_diff():
        print("\n⚠️  Smart diff test failed")
    
    print("\n" + "=" * 60)
    print("✅ Tests completed")

if __name__ == "__main__":
    main()