"""
Tests for security components.

This module contains unit tests for Lakera Guard integration and security management.
"""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from simple_mcp_client.security import (
    LakeraClient,
    LakeraGuardRequest,
    LakeraGuardResponse,
    SecurityManager,
    SecurityViolation,
)


class TestLakeraGuardRequest:
    """Test cases for LakeraGuardRequest model."""
    
    def test_lakera_guard_request_creation(self):
        """Test creating a LakeraGuardRequest with basic parameters."""
        messages = [{"role": "user", "content": "test content"}]
        request = LakeraGuardRequest(messages=messages)
        assert request.messages == messages
        assert request.dev_info is False
    
    def test_lakera_guard_request_with_dev_info(self):
        """Test creating a LakeraGuardRequest with dev_info enabled."""
        messages = [{"role": "user", "content": "test content"}]
        request = LakeraGuardRequest(messages=messages, dev_info=True)
        assert request.messages == messages
        assert request.dev_info is True


class TestLakeraGuardResponse:
    """Test cases for LakeraGuardResponse model."""
    
    def test_lakera_guard_response_creation(self):
        """Test creating a LakeraGuardResponse with basic parameters."""
        response = LakeraGuardResponse(flagged=False)
        assert response.flagged is False
        assert response.categories == {}
        assert response.category_scores == {}
        assert response.dev_info is None
    
    def test_lakera_guard_response_with_categories(self):
        """Test creating a LakeraGuardResponse with categories."""
        categories = {"prompt_injection": True, "jailbreaking": False}
        scores = {"prompt_injection": 0.8, "jailbreaking": 0.1}
        response = LakeraGuardResponse(
            flagged=True,
            categories=categories,
            category_scores=scores
        )
        assert response.flagged is True
        assert response.categories == categories
        assert response.category_scores == scores


class TestLakeraClient:
    """Test cases for LakeraClient class."""
    
    @patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'})
    def test_client_initialization(self):
        """Test LakeraClient initialization."""
        client = LakeraClient()
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.lakera.ai/v2"
        assert client.timeout == 30
        assert client.session.headers["Authorization"] == "Bearer test-key"
    
    def test_client_initialization_with_custom_params(self):
        """Test LakeraClient initialization with custom parameters."""
        client = LakeraClient(
            api_key="custom-key",
            base_url="https://custom.api.lakera.ai/v2",
            region="us-east-1",
            timeout=60
        )
        assert client.api_key == "custom-key"
        assert client.base_url == "https://us-east-1.api.lakera.ai/v2"
        assert client.timeout == 60
    
    def test_client_initialization_no_api_key(self):
        """Test LakeraClient initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Lakera API key is required"):
                LakeraClient()
    
    @patch('requests.Session.post')
    def test_screen_content_success(self, mock_post):
        """Test successful content screening."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "flagged": False,
            "categories": {},
            "category_scores": {}
        }
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            response = client.screen_content("test content")
            
            assert isinstance(response, LakeraGuardResponse)
            assert response.flagged is False
            
            # Verify the request was sent correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            request_data = json.loads(call_args[1]['json'])
            assert request_data["messages"] == [{"role": "user", "content": "test content"}]
    
    @patch('requests.Session.post')
    def test_screen_content_flagged(self, mock_post):
        """Test content screening with flagged content."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "flagged": True,
            "categories": {"prompt_injection": True},
            "category_scores": {"prompt_injection": 0.9}
        }
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            response = client.screen_content("test content")
            
            assert response.flagged is True
            assert response.categories["prompt_injection"] is True
            assert response.category_scores["prompt_injection"] == 0.9
    
    @patch('requests.Session.post')
    def test_screen_content_with_messages(self, mock_post):
        """Test content screening with message list."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "flagged": False,
            "categories": {},
            "category_scores": {}
        }
        mock_post.return_value = mock_response
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            response = client.screen_content(messages)
            
            # Verify the request was sent correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            request_data = json.loads(call_args[1]['json'])
            assert request_data["messages"] == messages
    
    @patch('requests.Session.post')
    def test_screen_content_error(self, mock_post):
        """Test content screening with API error."""
        mock_post.side_effect = requests.RequestException("API Error")
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            with pytest.raises(requests.RequestException):
                client.screen_content("test content")
    
    @patch('requests.Session.post')
    def test_screen_tool_description(self, mock_post):
        """Test tool description screening."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "flagged": False,
            "categories": {},
            "category_scores": {}
        }
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            response = client.screen_tool_description("Test tool description")
            
            assert isinstance(response, LakeraGuardResponse)
            assert response.flagged is False
    
    @patch('requests.Session.post')
    def test_screen_server_interaction(self, mock_post):
        """Test server interaction screening."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "flagged": False,
            "categories": {},
            "category_scores": {}
        }
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            response = client.screen_server_interaction("tools/list", {"param": "value"})
            
            assert isinstance(response, LakeraGuardResponse)
            assert response.flagged is False
    
    @patch('requests.Session.post')
    def test_is_content_safe(self, mock_post):
        """Test is_content_safe method."""
        mock_response = Mock()
        mock_response.json.return_value = {"flagged": False}
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            assert client.is_content_safe("safe content") is True
    
    @patch('requests.Session.post')
    def test_is_content_safe_flagged(self, mock_post):
        """Test is_content_safe method with flagged content."""
        mock_response = Mock()
        mock_response.json.return_value = {"flagged": True}
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'}):
            client = LakeraClient()
            assert client.is_content_safe("unsafe content") is False


class TestSecurityManager:
    """Test cases for SecurityManager class."""
    
    @patch.dict('os.environ', {'LAKERA_GUARD_API_KEY': 'test-key'})
    def test_security_manager_initialization(self):
        """Test SecurityManager initialization."""
        manager = SecurityManager()
        assert manager.enable_tool_screening is True
        assert manager.enable_interaction_screening is True
        assert manager.fail_on_violation is True
        assert manager.lakera_client is not None
    
    def test_security_manager_with_custom_client(self):
        """Test SecurityManager initialization with custom Lakera client."""
        mock_client = Mock()
        manager = SecurityManager(
            lakera_client=mock_client,
            enable_tool_screening=False,
            enable_interaction_screening=False,
            fail_on_violation=False
        )
        assert manager.lakera_client == mock_client
        assert manager.enable_tool_screening is False
        assert manager.enable_interaction_screening is False
        assert manager.fail_on_violation is False
    
    @patch('simple_mcp_client.security.security_manager.LakeraClient')
    def test_screen_tool_registration_safe(self, mock_lakera_client_class):
        """Test tool registration screening with safe content."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.flagged = False
        mock_client.screen_tool_description.return_value = mock_response
        mock_lakera_client_class.return_value = mock_client
        
        manager = SecurityManager(lakera_client=mock_client)
        result = manager.screen_tool_registration("test_tool", "safe description")
        
        assert result is True
        assert manager.screening_stats["tools_screened"] == 1
        assert manager.screening_stats["violations_detected"] == 0
    
    @patch('simple_mcp_client.security.security_manager.LakeraClient')
    def test_screen_tool_registration_flagged(self, mock_lakera_client_class):
        """Test tool registration screening with flagged content."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.flagged = True
        mock_response.categories = {"prompt_injection": True}
        mock_response.category_scores = {"prompt_injection": 0.9}
        mock_client.screen_tool_description.return_value = mock_response
        mock_lakera_client_class.return_value = mock_client
        
        manager = SecurityManager(lakera_client=mock_client)
        
        with pytest.raises(SecurityViolation):
            manager.screen_tool_registration("test_tool", "unsafe description")
        
        assert manager.screening_stats["tools_screened"] == 1
        assert manager.screening_stats["violations_detected"] == 1
    
    @patch('simple_mcp_client.security.security_manager.LakeraClient')
    def test_screen_tool_registration_flagged_no_fail(self, mock_lakera_client_class):
        """Test tool registration screening with flagged content but no failure."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.flagged = True
        mock_response.categories = {"prompt_injection": True}
        mock_client.screen_tool_description.return_value = mock_response
        mock_lakera_client_class.return_value = mock_client
        
        manager = SecurityManager(lakera_client=mock_client, fail_on_violation=False)
        result = manager.screen_tool_registration("test_tool", "unsafe description")
        
        assert result is False
        assert manager.screening_stats["violations_detected"] == 1
    
    @patch('simple_mcp_client.security.security_manager.LakeraClient')
    def test_screen_server_interaction_safe(self, mock_lakera_client_class):
        """Test server interaction screening with safe content."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.flagged = False
        mock_client.screen_server_interaction.return_value = mock_response
        mock_lakera_client_class.return_value = mock_client
        
        manager = SecurityManager(lakera_client=mock_client)
        result = manager.screen_server_interaction("tools/list", {"param": "value"})
        
        assert result is True
        assert manager.screening_stats["interactions_screened"] == 1
    
    @patch('simple_mcp_client.security.security_manager.LakeraClient')
    def test_screen_tools_list(self, mock_lakera_client_class):
        """Test screening a list of tools."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.flagged = False
        mock_client.screen_tool_description.return_value = mock_response
        mock_lakera_client_class.return_value = mock_client
        
        tools = [
            {"name": "tool1", "description": "safe tool"},
            {"name": "tool2", "description": "another safe tool"}
        ]
        
        manager = SecurityManager(lakera_client=mock_client)
        safe_tools = manager.screen_tools_list(tools)
        
        assert len(safe_tools) == 2
        assert manager.screening_stats["tools_screened"] == 2
    
    def test_get_screening_stats(self):
        """Test getting screening statistics."""
        manager = SecurityManager()
        stats = manager.get_screening_stats()
        
        expected_keys = ["tools_screened", "interactions_screened", "violations_detected", "screening_errors"]
        for key in expected_keys:
            assert key in stats
            assert isinstance(stats[key], int)
    
    def test_reset_stats(self):
        """Test resetting screening statistics."""
        manager = SecurityManager()
        manager.screening_stats["tools_screened"] = 5
        manager.screening_stats["violations_detected"] = 2
        
        manager.reset_stats()
        
        assert manager.screening_stats["tools_screened"] == 0
        assert manager.screening_stats["violations_detected"] == 0


class TestSecurityViolation:
    """Test cases for SecurityViolation exception."""
    
    def test_security_violation_creation(self):
        """Test creating a SecurityViolation exception."""
        categories = {"prompt_injection": True}
        scores = {"prompt_injection": 0.9}
        
        violation = SecurityViolation("Test violation", categories, scores)
        
        assert str(violation) == "Test violation"
        assert violation.categories == categories
        assert violation.scores == scores 