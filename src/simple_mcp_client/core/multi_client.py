"""
Multi-server MCP client implementation.

This module provides a client that can manage multiple MCP servers
and intelligently route tool requests to the appropriate server.
"""

import logging
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from .client import MCPClient
from ..security import SecurityManager, SecurityViolation

logger = logging.getLogger(__name__)


class MCPTool:
    """Represents a tool available from an MCP server."""
    
    def __init__(self, name: str, description: str, server_url: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.server_url = server_url
        self.parameters = parameters or {}
    
    def __repr__(self):
        return f"MCPTool(name='{self.name}', server='{self.server_url}')"


class MCPServer:
    """Represents an MCP server with its tools."""
    
    def __init__(self, url: str, client: MCPClient):
        self.url = url
        self.client = client
        self.tools: List[MCPTool] = []
        self.connected = False
    
    def __repr__(self):
        return f"MCPServer(url='{self.url}', tools={len(self.tools)})"


class MultiMCPClient:
    """
    Multi-server MCP client that can manage multiple servers and route tool requests.
    
    This client provides:
    - Multiple server management
    - Tool discovery across all servers
    - Intelligent tool routing
    - Unified tool interface
    """
    
    def __init__(
        self,
        security_manager: Optional[SecurityManager] = None,
        enable_security: bool = True,
        timeout: int = 30
    ):
        """
        Initialize the multi-server MCP client.
        
        Args:
            security_manager: Security manager instance
            enable_security: Whether to enable security screening
            timeout: Request timeout in seconds
        """
        self.servers: Dict[str, MCPServer] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.security_manager = security_manager
        self.enable_security = enable_security
        self.timeout = timeout
        
        # Statistics
        self.stats = {
            "servers_added": 0,
            "tools_discovered": 0,
            "requests_routed": 0,
            "routing_errors": 0
        }
    
    def add_server(self, server_url: str) -> bool:
        """
        Add an MCP server to the client.
        
        Args:
            server_url: URL of the MCP server
            
        Returns:
            True if server was added successfully, False otherwise
        """
        try:
            # Normalize URL
            parsed_url = urlparse(server_url)
            normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if normalized_url in self.servers:
                logger.warning(f"Server {normalized_url} already exists")
                return False
            
            # Create client for this server
            client = MCPClient(
                normalized_url,
                timeout=self.timeout,
                security_manager=self.security_manager,
                enable_security=self.enable_security
            )
            
            # Test connection
            if not client.connect():
                logger.error(f"Failed to connect to server {normalized_url}")
                return False
            
            # Create server instance
            server = MCPServer(normalized_url, client)
            server.connected = True
            
            # Discover tools
            self._discover_tools(server)
            
            # Add to servers
            self.servers[normalized_url] = server
            self.stats["servers_added"] += 1
            
            logger.info(f"Added server {normalized_url} with {len(server.tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Error adding server {server_url}: {e}")
            return False
    
    def remove_server(self, server_url: str) -> bool:
        """
        Remove an MCP server from the client.
        
        Args:
            server_url: URL of the MCP server
            
        Returns:
            True if server was removed successfully, False otherwise
        """
        parsed_url = urlparse(server_url)
        normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if normalized_url not in self.servers:
            return False
        
        server = self.servers[normalized_url]
        
        # Remove tools from this server
        tools_to_remove = [name for name, tool in self.tools.items() if tool.server_url == normalized_url]
        for tool_name in tools_to_remove:
            del self.tools[tool_name]
        
        # Close client and remove server
        server.client.close()
        del self.servers[normalized_url]
        
        logger.info(f"Removed server {normalized_url}")
        return True
    
    def _discover_tools(self, server: MCPServer):
        """Discover tools from a server."""
        try:
            response = server.client.list_tools()
            if response.error:
                logger.error(f"Error listing tools from {server.url}: {response.error}")
                return
            
            tools_data = response.result.get('tools', [])
            server.tools.clear()
            
            for tool_data in tools_data:
                tool = MCPTool(
                    name=tool_data.get('name', 'Unknown'),
                    description=tool_data.get('description', ''),
                    server_url=server.url,
                    parameters=tool_data.get('parameters')
                )
                
                server.tools.append(tool)
                self.tools[tool.name] = tool
                self.stats["tools_discovered"] += 1
            
        except Exception as e:
            logger.error(f"Error discovering tools from {server.url}: {e}")
    
    def refresh_tools(self, server_url: Optional[str] = None):
        """
        Refresh tool discovery for servers.
        
        Args:
            server_url: Specific server URL to refresh, or None for all servers
        """
        if server_url:
            parsed_url = urlparse(server_url)
            normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if normalized_url in self.servers:
                self._discover_tools(self.servers[normalized_url])
        else:
            # Refresh all servers
            for server in self.servers.values():
                self._discover_tools(server)
    
    def list_tools(self) -> List[MCPTool]:
        """
        Get all available tools across all servers.
        
        Returns:
            List of all available tools
        """
        return list(self.tools.values())
    
    def find_tool(self, tool_name: str) -> Optional[MCPTool]:
        """
        Find a specific tool by name.
        
        Args:
            tool_name: Name of the tool to find
            
        Returns:
            MCPTool instance if found, None otherwise
        """
        return self.tools.get(tool_name)
    
    def search_tools(self, query: str) -> List[MCPTool]:
        """
        Search for tools by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        matches = []
        
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matches.append(tool)
        
        return matches
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """
        Call a tool by name, automatically routing to the correct server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool response
            
        Raises:
            ValueError: If tool is not found
            SecurityViolation: If security screening detects a threat
        """
        tool = self.find_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        server = self.servers.get(tool.server_url)
        if not server:
            raise ValueError(f"Server for tool '{tool_name}' not available")
        
        try:
            self.stats["requests_routed"] += 1
            response = server.client.call_tool(tool_name, arguments)
            return response
            
        except Exception as e:
            self.stats["routing_errors"] += 1
            logger.error(f"Error calling tool '{tool_name}': {e}")
            raise
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about all servers.
        
        Returns:
            Dictionary with server information
        """
        info = {}
        for url, server in self.servers.items():
            info[url] = {
                "connected": server.connected,
                "tool_count": len(server.tools),
                "tools": [tool.name for tool in server.tools]
            }
        return info
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics.
        
        Returns:
            Dictionary with client statistics
        """
        stats = self.stats.copy()
        stats.update({
            "total_servers": len(self.servers),
            "total_tools": len(self.tools)
        })
        return stats
    
    def close(self):
        """Close all server connections."""
        for server in self.servers.values():
            server.client.close()
        self.servers.clear()
        self.tools.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 