#!/usr/bin/env python3
"""Audit script to find all missing GitLab client methods"""

import re
import ast
import sys
from pathlib import Path

def extract_handler_calls(handlers_file):
    """Extract all client method calls from tool handlers"""
    with open(handlers_file, 'r') as f:
        content = f.read()
    
    # Find all return client.method_name(...) calls
    pattern = r'return client\.(\w+)\('
    calls = re.findall(pattern, content)
    
    # Also find client.method_name calls in other contexts
    pattern2 = r'client\.(\w+)\('
    calls.extend(re.findall(pattern2, content))
    
    return set(calls)

def extract_client_methods(client_file):
    """Extract all defined methods in GitLabClient"""
    with open(client_file, 'r') as f:
        tree = ast.parse(f.read())
    
    methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'GitLabClient':
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if not item.name.startswith('_'):  # Skip private methods
                        methods.add(item.name)
    return methods

def main():
    handlers_file = Path('/home/dev/IdeaProjects/mcp-gitlab/src/mcp_gitlab/tool_handlers.py')
    client_file = Path('/home/dev/IdeaProjects/mcp-gitlab/src/mcp_gitlab/gitlab_client.py')
    
    # Get all handler calls and client methods
    handler_calls = extract_handler_calls(handlers_file)
    client_methods = extract_client_methods(client_file)
    
    # Find missing methods
    missing = handler_calls - client_methods
    
    # Sort for better readability
    missing = sorted(missing)
    handler_calls = sorted(handler_calls)
    client_methods = sorted(client_methods)
    
    print("=== AUDIT RESULTS ===\n")
    print(f"Total handler calls: {len(handler_calls)}")
    print(f"Total client methods: {len(client_methods)}")
    print(f"Missing methods: {len(missing)}\n")
    
    if missing:
        print("MISSING METHODS:")
        for method in missing:
            print(f"  - {method}")
    else:
        print("✅ All handler methods are implemented!")
    
    # Also show methods that exist but aren't used
    unused = client_methods - handler_calls
    if unused:
        print(f"\nUNUSED CLIENT METHODS ({len(unused)}):")
        for method in sorted(unused)[:10]:  # Show first 10
            print(f"  - {method}")
        if len(unused) > 10:
            print(f"  ... and {len(unused) - 10} more")

if __name__ == "__main__":
    main()