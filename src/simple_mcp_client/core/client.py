"""
MCP Client implementation.

This module provides the main client class for interacting with MCP servers.
"""

import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field

from ..security import SecurityManager, SecurityViolation

logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    """Model for MCP requests."""
    
    method: str = Field(..., description="The MCP method to call")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Request parameters")
    id: Optional[str] = Field(default=None, description="Request ID")


class MCPResponse(BaseModel):
    """Model for MCP responses."""
    
    result: Optional[Dict[str, Any]] = Field(default=None, description="Response result")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")
    id: Optional[str] = Field(default=None, description="Response ID")


class MCPClient:
    """
    A simple client for interacting with MCP (Model Context Protocol) servers.
    
    This client provides a straightforward interface for connecting to MCP servers
    and sending requests. It handles basic HTTP communication and JSON-RPC formatting.
    It also integrates Lakera Guard security screening for safe interactions.
    """
    
    def __init__(
        self,
        server_url: str,
        timeout: int = 30,
        security_manager: Optional[SecurityManager] = None,
        enable_security: bool = True
    ):
        """
        Initialize the MCP client.
        
        Args:
            server_url: The URL of the MCP server
            timeout: Request timeout in seconds
            security_manager: Security manager instance (will create one if not provided)
            enable_security: Whether to enable security screening
        """
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.enable_security = enable_security
        
        # Initialize security manager if enabled
        self.security_manager = None
        if self.enable_security:
            self.security_manager = security_manager or SecurityManager()
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def connect(self) -> bool:
        """
        Test the connection to the MCP server.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.session.get(
                urljoin(self.server_url, '/health'),
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """
        Send a request to the MCP server with security screening.
        
        Args:
            method: The MCP method to call
            params: Optional parameters for the request
            
        Returns:
            MCPResponse object containing the server response
            
        Raises:
            requests.RequestException: If the request fails
            SecurityViolation: If security screening detects a threat
        """
        # Security screening for the request
        if self.security_manager:
            try:
                self.security_manager.screen_server_interaction(method, params)
            except SecurityViolation as e:
                logger.error(f"Security violation detected in request: {e}")
                raise
        
        request_data = MCPRequest(
            method=method,
            params=params or {},
            id="1"  # Simple ID for now
        )
        
        try:
            response = self.session.post(
                self.server_url,
                json=request_data.model_dump(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            response_data = response.json()
            mcp_response = MCPResponse(**response_data)
            
            # Security screening for the response
            if self.security_manager and mcp_response.result:
                try:
                    self.security_manager.screen_server_interaction(
                        method, params, mcp_response.result
                    )
                except SecurityViolation as e:
                    logger.error(f"Security violation detected in response: {e}")
                    raise
            
            return mcp_response
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def list_tools(self) -> MCPResponse:
        """
        List available tools from the MCP server with security screening.
        
        Returns:
            MCPResponse containing the list of tools (filtered for security)
        """
        response = self.send_request("tools/list")
        
        # Apply security screening to tools list
        if self.security_manager and response.result:
            tools = response.result.get('tools', [])
            safe_tools = self.security_manager.screen_tools_list(tools)
            response.result['tools'] = safe_tools
            
            # Log screening results
            stats = self.security_manager.get_screening_stats()
            if stats['tools_screened'] > 0:
                logger.info(f"Security screening: {stats['tools_screened']} tools screened, "
                          f"{stats['violations_detected']} violations detected")
        
        return response
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """
        Call a specific tool on the MCP server with security screening.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            MCPResponse containing the tool result
        """
        return self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    def get_security_stats(self) -> Optional[Dict[str, int]]:
        """
        Get security screening statistics.
        
        Returns:
            Dictionary with screening statistics or None if security is disabled
        """
        if self.security_manager:
            return self.security_manager.get_screening_stats()
        return None
    
    def close(self):
        """Close the client session and security manager."""
        self.session.close()
        if self.security_manager:
            self.security_manager.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 