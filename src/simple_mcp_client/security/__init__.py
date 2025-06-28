"""
Security module for the Simple MCP Client.

This module provides security screening capabilities using Lakera Guard
to ensure safe interactions with MCP servers.
"""

from .lakera_client import LakeraClient
from .security_manager import SecurityManager, SecurityViolation

__all__ = ["LakeraClient", "SecurityManager", "SecurityViolation"] 