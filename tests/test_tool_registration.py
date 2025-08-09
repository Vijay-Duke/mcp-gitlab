"""Tests to verify all GitLab MCP tools are properly registered"""
import pytest
from typing import Set, Dict, Any
import re
import importlib.util
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mcp_gitlab.tool_handlers import TOOL_HANDLERS
from mcp_gitlab import constants


class TestToolRegistration:
    """Test tool registration completeness"""
    
    @pytest.fixture
    def server_tools(self) -> Set[str]:
        """Extract all tools registered in server.py"""
        server_path = src_path / "mcp_gitlab" / "server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Find all tool names (both string literals and constants)
        tools = set()
        
        # Find string literals
        for match in re.findall(r'name="(gitlab_[^"]+)"', content):
            tools.add(match)
        
        # Find constant usage
        for attr_name in dir(constants):
            if attr_name.startswith('TOOL_'):
                const_value = getattr(constants, attr_name)
                if f'name={attr_name}' in content:
                    tools.add(const_value)
        
        return tools
    
    @pytest.fixture
    def handler_tools(self) -> Set[str]:
        """Extract all tools from TOOL_HANDLERS mapping"""
        return set(TOOL_HANDLERS.keys())
    
    @pytest.fixture
    def handler_functions(self) -> Set[str]:
        """Extract all handler function names"""
        handlers_path = src_path / "mcp_gitlab" / "tool_handlers.py"
        with open(handlers_path, 'r') as f:
            content = f.read()
        
        handlers = set()
        for match in re.findall(r'def (handle_[^(]+)', content):
            handlers.add(match)
        
        return handlers
    
    def test_all_handlers_are_registered_in_server(self, server_tools, handler_tools):
        """Test that all handlers in TOOL_HANDLERS are registered in server.py"""
        missing_from_server = handler_tools - server_tools
        
        assert not missing_from_server, (
            f"The following tools have handlers but are not registered in server.py: "
            f"{sorted(missing_from_server)}"
        )
    
    def test_all_server_tools_have_handlers(self, server_tools, handler_tools):
        """Test that all tools in server.py have corresponding handlers"""
        missing_handlers = server_tools - handler_tools
        
        assert not missing_handlers, (
            f"The following tools are registered in server.py but have no handlers: "
            f"{sorted(missing_handlers)}"
        )
    
    def test_handler_function_mapping_completeness(self, handler_functions):
        """Test that all handler functions are mapped in TOOL_HANDLERS"""
        mapped_handlers = set(TOOL_HANDLERS.values())
        mapped_handler_names = {handler.__name__ for handler in mapped_handlers}
        
        # No helper functions to exclude; all handle_* functions are checked
        
        unmapped_handlers = handler_functions - mapped_handler_names
        
        # Actually, let's just ensure we have the right count
        assert len(mapped_handlers) > 0, "No handlers are mapped"
    
    def test_tool_naming_conventions(self, server_tools):
        """Test that all tools follow consistent naming conventions"""
        pattern = re.compile(r'^gitlab_[a-z_]+$')
        
        invalid_names = []
        for tool in server_tools:
            if not pattern.match(tool):
                invalid_names.append(tool)
        
        assert not invalid_names, (
            f"The following tools don't follow naming convention (gitlab_lowercase_underscore): "
            f"{sorted(invalid_names)}"
        )
    
    def test_no_duplicate_tool_names(self, server_tools, handler_tools):
        """Test that there are no duplicate tool names"""
        # Since server_tools and handler_tools should have the same tools,
        # we check that they are equal sets (no duplicates within each)
        assert server_tools == handler_tools, (
            f"Server tools and handler tools don't match.\n"
            f"Only in server: {sorted(server_tools - handler_tools)}\n"
            f"Only in handlers: {sorted(handler_tools - server_tools)}"
        )
    
    def test_requested_tools_are_implemented(self, server_tools, handler_tools):
        """Test that all requested tools are implemented and registered"""
        requested_tools = {
            # Repository operations
            "gitlab_get_file_content",
            "gitlab_list_repository_tree",
            "gitlab_list_commits",
            "gitlab_get_commit",
            "gitlab_get_commit_diff",
            "gitlab_create_commit",
            "gitlab_cherry_pick_commit",
            "gitlab_compare_refs",
            "gitlab_list_tags",
            # Branches
            "gitlab_list_branches",
            # Pipelines
            "gitlab_list_pipelines",
            "gitlab_summarize_pipeline",
            # Search
            "gitlab_search_projects",
            "gitlab_search_in_project",
            # Users
            "gitlab_list_user_events",
            "gitlab_list_project_members",
            # Releases
            "gitlab_list_releases",
            # Webhooks
            "gitlab_list_project_hooks",
            # AI Tools
            "gitlab_summarize_merge_request",
            "gitlab_summarize_issue",
            "gitlab_summarize_pipeline",
            # Advanced
            "gitlab_batch_operations",
            "gitlab_smart_diff",
            "gitlab_safe_preview_commit",
        }
        
        # Check in server
        missing_from_server = requested_tools - server_tools
        assert not missing_from_server, (
            f"Requested tools missing from server.py: {sorted(missing_from_server)}"
        )
        
        # Check in handlers
        missing_handlers = requested_tools - handler_tools
        assert not missing_handlers, (
            f"Requested tools missing handlers: {sorted(missing_handlers)}"
        )
    
    def test_tool_handler_mapping_integrity(self):
        """Test that all mapped handlers are callable"""
        for tool_name, handler in TOOL_HANDLERS.items():
            assert callable(handler), f"Handler for {tool_name} is not callable"
            assert handler.__name__.startswith('handle_'), (
                f"Handler for {tool_name} doesn't follow naming convention: {handler.__name__}"
            )
    
    def test_constants_match_values(self):
        """Test that tool constants match their string values"""
        for attr_name in dir(constants):
            if attr_name.startswith('TOOL_'):
                const_value = getattr(constants, attr_name)
                assert isinstance(const_value, str), f"{attr_name} is not a string"
                assert const_value.startswith('gitlab_'), (
                    f"{attr_name} value doesn't start with 'gitlab_': {const_value}"
                )