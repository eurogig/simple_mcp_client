"""
Tests for the MCPClient class.

This module contains unit tests for the main client functionality.
"""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from simple_mcp_client.core.client import MCPClient, MCPRequest, MCPResponse


class TestMCPRequest:
    """Test cases for MCPRequest model."""
    
    def test_mcp_request_creation(self):
        """Test creating an MCPRequest with basic parameters."""
        request = MCPRequest(method="tools/list")
        assert request.method == "tools/list"
        assert request.params is None
        assert request.id is None
    
    def test_mcp_request_with_params(self):
        """Test creating an MCPRequest with parameters."""
        params = {"name": "test_tool"}
        request = MCPRequest(method="tools/call", params=params, id="123")
        assert request.method == "tools/call"
        assert request.params == params
        assert request.id == "123"


class TestMCPResponse:
    """Test cases for MCPResponse model."""
    
    def test_mcp_response_creation(self):
        """Test creating an MCPResponse with basic parameters."""
        response = MCPResponse(result={"tools": []})
        assert response.result == {"tools": []}
        assert response.error is None
        assert response.id is None
    
    def test_mcp_response_with_error(self):
        """Test creating an MCPResponse with error information."""
        error = {"code": 404, "message": "Not found"}
        response = MCPResponse(error=error, id="123")
        assert response.error == error
        assert response.result is None
        assert response.id == "123"


class TestMCPClient:
    """Test cases for MCPClient class."""
    
    def test_client_initialization(self):
        """Test MCPClient initialization."""
        client = MCPClient("http://localhost:8000")
        assert client.server_url == "http://localhost:8000"
        assert client.timeout == 30
        assert client.session.headers["Content-Type"] == "application/json"
        assert client.session.headers["Accept"] == "application/json"
    
    def test_client_initialization_with_timeout(self):
        """Test MCPClient initialization with custom timeout."""
        client = MCPClient("http://localhost:8000", timeout=60)
        assert client.timeout == 60
    
    def test_client_url_normalization(self):
        """Test that URLs are properly normalized."""
        client = MCPClient("http://localhost:8000/")
        assert client.server_url == "http://localhost:8000"
    
    @patch('requests.Session.get')
    def test_connect_success(self, mock_get):
        """Test successful connection to MCP server."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        assert client.connect() is True
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_connect_failure(self, mock_get):
        """Test failed connection to MCP server."""
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        client = MCPClient("http://localhost:8000")
        assert client.connect() is False
    
    @patch('requests.Session.post')
    def test_send_request_success(self, mock_post):
        """Test successful request sending."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"tools": ["tool1", "tool2"]},
            "id": "1"
        }
        mock_post.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        response = client.send_request("tools/list")
        
        assert isinstance(response, MCPResponse)
        assert response.result == {"tools": ["tool1", "tool2"]}
        assert response.id == "1"
        
        # Verify the request was sent correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:8000"
        
        request_data = json.loads(call_args[1]['json'])
        assert request_data["method"] == "tools/list"
        assert request_data["params"] == {}
    
    @patch('requests.Session.post')
    def test_send_request_with_params(self, mock_post):
        """Test request sending with parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"success": True},
            "id": "1"
        }
        mock_post.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        params = {"name": "test_tool", "arguments": {"arg1": "value1"}}
        response = client.send_request("tools/call", params)
        
        assert response.result == {"success": True}
        
        # Verify parameters were sent correctly
        call_args = mock_post.call_args
        request_data = json.loads(call_args[1]['json'])
        assert request_data["params"] == params
    
    @patch('requests.Session.post')
    def test_send_request_error(self, mock_post):
        """Test request sending with server error."""
        mock_post.side_effect = requests.RequestException("Request failed")
        
        client = MCPClient("http://localhost:8000")
        with pytest.raises(requests.RequestException):
            client.send_request("tools/list")
    
    @patch('requests.Session.post')
    def test_list_tools(self, mock_post):
        """Test list_tools method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"tools": [{"name": "tool1"}, {"name": "tool2"}]},
            "id": "1"
        }
        mock_post.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        response = client.list_tools()
        
        assert response.result == {"tools": [{"name": "tool1"}, {"name": "tool2"}]}
        
        # Verify the correct method was called
        call_args = mock_post.call_args
        request_data = json.loads(call_args[1]['json'])
        assert request_data["method"] == "tools/list"
    
    @patch('requests.Session.post')
    def test_call_tool(self, mock_post):
        """Test call_tool method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {"output": "tool result"},
            "id": "1"
        }
        mock_post.return_value = mock_response
        
        client = MCPClient("http://localhost:8000")
        arguments = {"input": "test input"}
        response = client.call_tool("test_tool", arguments)
        
        assert response.result == {"output": "tool result"}
        
        # Verify the correct method and parameters were sent
        call_args = mock_post.call_args
        request_data = json.loads(call_args[1]['json'])
        assert request_data["method"] == "tools/call"
        assert request_data["params"]["name"] == "test_tool"
        assert request_data["params"]["arguments"] == arguments
    
    def test_context_manager(self):
        """Test client as context manager."""
        with MCPClient("http://localhost:8000") as client:
            assert isinstance(client, MCPClient)
            # Session should be closed when exiting context
            assert not client.session.closed
        
        # Session should be closed after context exit
        assert client.session.closed
    
    def test_close_method(self):
        """Test client close method."""
        client = MCPClient("http://localhost:8000")
        assert not client.session.closed
        client.close()
        assert client.session.closed 