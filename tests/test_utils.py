"""
Tests for utility functions.

This module contains unit tests for helper functions.
"""

import json
import pytest

from simple_mcp_client.utils.helpers import (
    format_request,
    parse_response,
    validate_url,
    safe_json_loads,
)


class TestFormatRequest:
    """Test cases for format_request function."""
    
    def test_format_request_basic(self):
        """Test formatting a basic request."""
        result = format_request("tools/list")
        expected = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "1"
        }
        assert result == expected
    
    def test_format_request_with_params(self):
        """Test formatting a request with parameters."""
        params = {"name": "test_tool"}
        result = format_request("tools/call", params)
        expected = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": params,
            "id": "1"
        }
        assert result == expected
    
    def test_format_request_with_custom_id(self):
        """Test formatting a request with custom ID."""
        result = format_request("tools/list", request_id="123")
        expected = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "123"
        }
        assert result == expected


class TestParseResponse:
    """Test cases for parse_response function."""
    
    def test_parse_response_success(self):
        """Test parsing a successful response."""
        response_data = {
            "jsonrpc": "2.0",
            "result": {"tools": ["tool1", "tool2"]},
            "id": "1"
        }
        result = parse_response(response_data)
        assert result == {"tools": ["tool1", "tool2"]}
    
    def test_parse_response_no_result(self):
        """Test parsing a response with no result."""
        response_data = {
            "jsonrpc": "2.0",
            "id": "1"
        }
        result = parse_response(response_data)
        assert result == {}
    
    def test_parse_response_invalid_format(self):
        """Test parsing an invalid response format."""
        response_data = {
            "result": {"data": "test"}
        }
        with pytest.raises(ValueError, match="Invalid JSON-RPC response format"):
            parse_response(response_data)
    
    def test_parse_response_with_error(self):
        """Test parsing a response with error."""
        response_data = {
            "jsonrpc": "2.0",
            "error": {
                "code": 404,
                "message": "Not found"
            },
            "id": "1"
        }
        with pytest.raises(ValueError, match="MCP Error 404: Not found"):
            parse_response(response_data)


class TestValidateUrl:
    """Test cases for validate_url function."""
    
    def test_validate_url_valid_http(self):
        """Test validating a valid HTTP URL."""
        assert validate_url("http://localhost:8000") is True
    
    def test_validate_url_valid_https(self):
        """Test validating a valid HTTPS URL."""
        assert validate_url("https://api.example.com") is True
    
    def test_validate_url_invalid_protocol(self):
        """Test validating a URL with invalid protocol."""
        assert validate_url("ftp://localhost:8000") is False
    
    def test_validate_url_no_protocol(self):
        """Test validating a URL without protocol."""
        assert validate_url("localhost:8000") is False
    
    def test_validate_url_empty(self):
        """Test validating an empty URL."""
        assert validate_url("") is False
    
    def test_validate_url_none(self):
        """Test validating a None URL."""
        assert validate_url(None) is False


class TestSafeJsonLoads:
    """Test cases for safe_json_loads function."""
    
    def test_safe_json_loads_valid(self):
        """Test parsing valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = safe_json_loads(json_str)
        expected = {"key": "value", "number": 42}
        assert result == expected
    
    def test_safe_json_loads_invalid_json(self):
        """Test parsing invalid JSON."""
        json_str = '{"key": "value", "number": 42'  # Missing closing brace
        result = safe_json_loads(json_str)
        assert result is None
    
    def test_safe_json_loads_empty_string(self):
        """Test parsing empty string."""
        result = safe_json_loads("")
        assert result is None
    
    def test_safe_json_loads_none(self):
        """Test parsing None."""
        result = safe_json_loads(None)
        assert result is None
    
    def test_safe_json_loads_complex_data(self):
        """Test parsing complex JSON data."""
        json_str = '''
        {
            "tools": [
                {
                    "name": "tool1",
                    "description": "First tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string"}
                        }
                    }
                }
            ]
        }
        '''
        result = safe_json_loads(json_str)
        assert result is not None
        assert "tools" in result
        assert len(result["tools"]) == 1
        assert result["tools"][0]["name"] == "tool1" 