#!/usr/bin/env python3
"""Simple GitLab connection test"""

import os
import gitlab
import traceback

def test():
    gitlab_url = "https://gitlab.com"
    private_token = "glpat-J3rFBaVyROuzIqG4MEShzG86MQp1OmRldmJzCw.01.120as5qmx"
    
    print(f"Testing connection to {gitlab_url}")
    
    try:
        # Create connection
        gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        print("✓ GitLab object created")
        
        # Try to authenticate
        gl.auth()
        print("✓ Authentication successful")
        
        # Try to list projects
        try:
            projects = gl.projects.list(per_page=1)
            print(f"✓ Found {len(projects)} project(s)")
            if projects:
                project = projects[0]
                print(f"  Project: {project.name}")
                
                # Try to get compare
                try:
                    comparison = project.repository_compare("master", "main")
                    print("✓ Compare API works")
                except Exception as e:
                    print(f"  Compare test: {e}")
        except AttributeError as e:
            print(f"⚠️  Projects API issue: {e}")
            print("  Trying alternative approach...")
            
            # Try direct API call
            response = gl.http_list("/projects", {"per_page": 1})
            print(f"✓ Direct API call worked: {len(response)} projects")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test()