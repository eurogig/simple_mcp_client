"""
Helper utilities for the MCP client.

This module provides utility functions for formatting requests and parsing responses.
"""

import json
from typing import Any, Dict, Optional


def format_request(method: str, params: Optional[Dict[str, Any]] = None, request_id: str = "1") -> Dict[str, Any]:
    """
    Format a request for the MCP server.
    
    Args:
        method: The MCP method to call
        params: Optional parameters for the request
        request_id: Unique identifier for the request
        
    Returns:
        Formatted request dictionary
    """
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "id": request_id
    }
    
    if params:
        request["params"] = params
        
    return request


def parse_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a response from the MCP server.
    
    Args:
        response_data: Raw response data from the server
        
    Returns:
        Parsed response dictionary
        
    Raises:
        ValueError: If the response format is invalid
    """
    if "jsonrpc" not in response_data or response_data["jsonrpc"] != "2.0":
        raise ValueError("Invalid JSON-RPC response format")
    
    if "error" in response_data:
        error = response_data["error"]
        raise ValueError(f"MCP Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")
    
    return response_data.get("result", {})


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    # Basic URL validation
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    return True


def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON data.
    
    Args:
        data: JSON string to parse
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None 