"""
Server configuration management.

This module provides configuration management for multiple MCP servers.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    
    name: str = Field(..., description="Human-readable name for the server")
    url: str = Field(..., description="Server URL")
    description: Optional[str] = Field(default=None, description="Server description")
    enabled: bool = Field(default=True, description="Whether the server is enabled")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    priority: int = Field(default=0, description="Priority for tool selection (higher = preferred)")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the server")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ClientConfig(BaseModel):
    """Configuration for the MCP client."""
    
    servers: List[ServerConfig] = Field(default_factory=list, description="List of server configurations")
    default_timeout: int = Field(default=30, description="Default timeout for servers")
    enable_security: bool = Field(default=True, description="Enable security screening by default")
    security_fail_on_violation: bool = Field(default=True, description="Fail on security violations")
    auto_discover: bool = Field(default=True, description="Automatically discover tools on server addition")
    refresh_interval: Optional[int] = Field(default=None, description="Tool refresh interval in seconds")


def get_config_path() -> Path:
    """Get the default configuration file path."""
    config_dir = Path.home() / ".simple_mcp_client"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_config(config_path: Optional[Path] = None) -> ClientConfig:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file, or None for default
        
    Returns:
        ClientConfig instance
    """
    if config_path is None:
        config_path = get_config_path()
    
    if not config_path.exists():
        # Return default configuration
        return ClientConfig()
    
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        return ClientConfig(**data)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        return ClientConfig()


def save_config(config: ClientConfig, config_path: Optional[Path] = None):
    """
    Save configuration to file.
    
    Args:
        config: ClientConfig instance to save
        config_path: Path to configuration file, or None for default
    """
    if config_path is None:
        config_path = get_config_path()
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config.model_dump(), f, indent=2)
    except Exception as e:
        print(f"Error saving config to {config_path}: {e}")


def add_server_config(
    name: str,
    url: str,
    description: Optional[str] = None,
    enabled: bool = True,
    timeout: int = 30,
    priority: int = 0,
    tags: Optional[List[str]] = None,
    config_path: Optional[Path] = None
) -> bool:
    """
    Add a server configuration.
    
    Args:
        name: Server name
        url: Server URL
        description: Server description
        enabled: Whether server is enabled
        timeout: Request timeout
        priority: Server priority
        tags: Server tags
        config_path: Configuration file path
        
    Returns:
        True if added successfully, False otherwise
    """
    config = load_config(config_path)
    
    # Check if server already exists
    for server in config.servers:
        if server.name == name or server.url == url:
            print(f"Server with name '{name}' or URL '{url}' already exists")
            return False
    
    # Create new server config
    server_config = ServerConfig(
        name=name,
        url=url,
        description=description,
        enabled=enabled,
        timeout=timeout,
        priority=priority,
        tags=tags or []
    )
    
    config.servers.append(server_config)
    save_config(config, config_path)
    
    print(f"Added server '{name}' ({url})")
    return True


def remove_server_config(name: str, config_path: Optional[Path] = None) -> bool:
    """
    Remove a server configuration.
    
    Args:
        name: Server name to remove
        config_path: Configuration file path
        
    Returns:
        True if removed successfully, False otherwise
    """
    config = load_config(config_path)
    
    for i, server in enumerate(config.servers):
        if server.name == name:
            removed_server = config.servers.pop(i)
            save_config(config, config_path)
            print(f"Removed server '{removed_server.name}' ({removed_server.url})")
            return True
    
    print(f"Server '{name}' not found")
    return False


def list_server_configs(config_path: Optional[Path] = None) -> List[ServerConfig]:
    """
    List all server configurations.
    
    Args:
        config_path: Configuration file path
        
    Returns:
        List of server configurations
    """
    config = load_config(config_path)
    return config.servers


def get_server_config(name: str, config_path: Optional[Path] = None) -> Optional[ServerConfig]:
    """
    Get a specific server configuration.
    
    Args:
        name: Server name
        config_path: Configuration file path
        
    Returns:
        ServerConfig if found, None otherwise
    """
    config = load_config(config_path)
    
    for server in config.servers:
        if server.name == name:
            return server
    
    return None 