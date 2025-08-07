"""Simplified tests for MCP server focusing on error handling and tool dispatch"""
import pytest
import json
from unittest.mock import Mock, patch
import gitlab.exceptions
import mcp.types as types
from mcp_gitlab.server import handle_list_tools, handle_call_tool, get_gitlab_client
from mcp_gitlab.tool_handlers import TOOL_HANDLERS
from mcp_gitlab.constants import (
    TOOL_LIST_PROJECTS, ERROR_AUTH_FAILED, ERROR_NOT_FOUND, 
    ERROR_RATE_LIMIT, ERROR_INVALID_INPUT, ERROR_GENERIC
)


class TestServerCore:
    """Test core server functionality"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock GitLabClient instance"""
        with patch('mcp_gitlab.server.get_gitlab_client') as mock:
            client = Mock()
            mock.return_value = client
            yield client
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_list_tools(self):
        """Test listing available tools"""
        tools = await handle_list_tools()
        
        # Check that tools are returned
        assert len(tools) > 0
        assert all(hasattr(tool, 'name') for tool in tools)
        assert all(hasattr(tool, 'description') for tool in tools)
        assert all(hasattr(tool, 'inputSchema') for tool in tools)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_success(self, mock_client):
        """Test successful tool execution"""
        mock_handler = Mock(return_value={"result": "success"})
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {"arg": "value"})
            
            mock_handler.assert_called_once_with(mock_client, {"arg": "value"})
            assert len(result) == 1
            assert json.loads(result[0].text) == {"result": "success"}
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_unknown(self, mock_client):
        """Test calling unknown tool"""
        result = await handle_call_tool("unknown_tool", {})
        
        response = json.loads(result[0].text)
        assert "error" in response
        assert response["error"] == ERROR_INVALID_INPUT
        assert response["type"] == "ValueError"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_authentication_error(self, mock_client):
        """Test handling authentication errors"""
        mock_handler = Mock(side_effect=gitlab.exceptions.GitlabAuthenticationError())
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {})
            
            response = json.loads(result[0].text)
            assert response["error"] == ERROR_AUTH_FAILED
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_not_found_error(self, mock_client):
        """Test handling 404 errors"""
        error = gitlab.exceptions.GitlabGetError()
        error.response_code = 404
        mock_handler = Mock(side_effect=error)
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {})
            
            response = json.loads(result[0].text)
            assert response["error"] == ERROR_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_rate_limit_error(self, mock_client):
        """Test handling rate limit errors"""
        error = gitlab.exceptions.GitlabGetError()
        error.response_code = 429
        mock_handler = Mock(side_effect=error)
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {})
            
            response = json.loads(result[0].text)
            assert "Rate limit exceeded" in response["error"]
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_gitlab_error(self, mock_client):
        """Test handling general GitLab errors"""
        mock_handler = Mock(side_effect=gitlab.exceptions.GitlabError("GitLab error"))
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {})
            
            response = json.loads(result[0].text)
            assert "error" in response
            assert response["error"] == ERROR_GENERIC
            assert response["type"] == "GitlabError"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_value_error(self, mock_client):
        """Test handling ValueError"""
        mock_handler = Mock(side_effect=ValueError("Invalid input"))
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {})
            
            response = json.loads(result[0].text)
            assert response["error"] == ERROR_INVALID_INPUT
            assert response["type"] == "ValueError"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_handle_call_tool_generic_error(self, mock_client):
        """Test handling generic exceptions"""
        mock_handler = Mock(side_effect=Exception("Unexpected"))
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {})
            
            response = json.loads(result[0].text)
            assert response["error"] == ERROR_GENERIC
            assert response["type"] == "Exception"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_response_truncation(self, mock_client):
        """Test that large responses are truncated"""
        # Create a large response
        large_data = {"data": ["item" + str(i) for i in range(10000)]}
        mock_handler = Mock(return_value=large_data)
        
        with patch.dict(TOOL_HANDLERS, {"test_tool": mock_handler}):
            result = await handle_call_tool("test_tool", {})
            
            response = json.loads(result[0].text)
            # Should be truncated
            assert "_truncated" in response or len(result[0].text) < 30000