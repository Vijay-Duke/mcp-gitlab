"""Tests for utility functions"""
import pytest
import time
from unittest.mock import Mock, patch
from mcp_gitlab.utils import (
    GitLabClientManager,
    sanitize_error, truncate_response
)
from mcp_gitlab.gitlab_client import GitLabClient, GitLabConfig
from mcp_gitlab.constants import CACHE_TTL_MEDIUM, MAX_RESPONSE_SIZE


class TestGitLabClientManager:
    """Test cases for GitLabClientManager singleton"""
    
    @pytest.mark.unit
    def test_singleton_instance(self):
        """Test that GitLabClientManager returns same instance"""
        manager1 = GitLabClientManager()
        manager2 = GitLabClientManager()
        
        assert manager1 is manager2
    
    @pytest.mark.unit
    @patch('mcp_gitlab.gitlab_client.GitLabClient')
    def test_get_client_creates_new(self, mock_client_class):
        """Test creating new client when none exists"""
        manager = GitLabClientManager()
        manager._instance = None  # Reset instance
        
        config = GitLabConfig(
            url="https://gitlab.com",
            private_token="test-token"
        )
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = manager.get_client(config)
        
        mock_client_class.assert_called_once_with(config)
        assert client is mock_client
    
    @pytest.mark.unit
    @patch('mcp_gitlab.gitlab_client.GitLabClient')
    def test_get_client_reuses_existing(self, mock_client_class):
        """Test reusing existing client with same config"""
        manager = GitLabClientManager()
        manager._instance = None  # Reset instance
        
        config = GitLabConfig(
            url="https://gitlab.com",
            private_token="test-token"
        )
        
        # First call creates client
        client1 = manager.get_client(config)
        
        # Second call should reuse
        client2 = manager.get_client(config)
        
        # Should only create one client
        assert mock_client_class.call_count == 1
        assert client1 is client2
    
    @pytest.mark.unit
    @patch('mcp_gitlab.gitlab_client.GitLabClient')
    def test_get_client_new_on_config_change(self, mock_client_class):
        """Test creating new client when config changes"""
        # Configure mock to return different instances for each call
        mock_client1 = Mock()
        mock_client2 = Mock()
        mock_client_class.side_effect = [mock_client1, mock_client2]
        
        # Reset singleton state
        GitLabClientManager._instance = None
        manager = GitLabClientManager()
        manager._client = None
        manager._config_hash = None
        
        config1 = GitLabConfig(
            url="https://gitlab.com",
            private_token="token1"
        )
        config2 = GitLabConfig(
            url="https://gitlab.com",
            private_token="token2"
        )
        
        client1 = manager.get_client(config1)
        client2 = manager.get_client(config2)
        
        # Should create two different clients
        assert mock_client_class.call_count == 2
        assert client1 is not client2



class TestErrorHandling:
    """Test cases for error handling utilities"""
    
    @pytest.mark.unit
    def test_sanitize_error_with_message(self):
        """Test sanitizing error with custom message"""
        error = Exception("Original error message")
        result = sanitize_error(error, "Custom error message")
        
        assert result["error"] == "Custom error message"
        assert result["type"] == "Exception"
    
    @pytest.mark.unit
    def test_sanitize_error_default_message(self):
        """Test sanitizing error with default message"""
        error = Exception("Some error")
        result = sanitize_error(error)
        
        assert result["error"] == "An unexpected error occurred. Please try again."
        assert result["type"] == "Exception"
    
    @pytest.mark.unit
    def test_sanitize_error_empty_exception(self):
        """Test sanitizing error with empty exception message"""
        error = Exception("")
        result = sanitize_error(error, "Custom message")
        
        assert result["error"] == "Custom message"
        assert result["type"] == "Exception"
    
    @pytest.mark.unit
    def test_truncate_response_dict(self):
        """Test truncating dictionary response"""
        data = {
            "key1": "a" * 1000,
            "key2": "b" * 1000,
            "key3": ["item1", "item2", "item3"]
        }
        
        result = truncate_response(data, max_size=100)
        
        # Should be truncated
        assert isinstance(result, dict)
        assert "truncated" in result
        assert result["truncated"] is True
        assert "message" in result
        assert "size" in result
    
    @pytest.mark.unit
    def test_truncate_response_list(self):
        """Test truncating list response"""
        data = ["item" + str(i) for i in range(1000)]
        
        result = truncate_response(data, max_size=100)
        
        # Should be truncated
        assert isinstance(result, dict)
        assert "truncated" in result
        assert result["truncated"] is True
        assert "data" in result
        assert len(result["data"]) < len(data)
    
    @pytest.mark.unit
    def test_truncate_response_string(self):
        """Test truncating string response (non-list/dict)"""
        data = "a" * 10000
        
        result = truncate_response(data, max_size=100)
        
        # String is not a list, so it returns truncation message
        assert isinstance(result, dict)
        assert result["truncated"] is True
        assert "message" in result
        assert "size" in result
    
    @pytest.mark.unit
    def test_truncate_response_within_limit(self):
        """Test response within limit is not truncated"""
        data = {"key": "value", "number": 42}
        
        result = truncate_response(data, max_size=10000)
        
        assert result == data  # Unchanged
    
    @pytest.mark.unit
    def test_truncate_response_special_cases(self):
        """Test truncating special data types"""
        # Small dict should not be truncated
        small_data = {"test": 123}
        assert truncate_response(small_data, max_size=1000) == small_data
        
        # Large list should be truncated
        large_list = list(range(10000))
        result = truncate_response(large_list, max_size=100)
        assert result["truncated"] is True
        assert "data" in result