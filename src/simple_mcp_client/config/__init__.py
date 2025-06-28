"""
Configuration management for the Simple MCP Client.

This module provides configuration management for multiple MCP servers.
"""

from .server_config import ServerConfig, load_config, save_config

__all__ = ["ServerConfig", "load_config", "save_config"] 