"""
Simple MCP Client - A lightweight client for the Model Context Protocol.

This package provides a simple and easy-to-use client implementation
for interacting with MCP (Model Context Protocol) servers.
"""

__version__ = "0.1.0"
__author__ = "Stephen Giguere"
__email__ = "your.email@example.com"

from .core.client import MCPClient
from .security import SecurityManager, SecurityViolation, LakeraClient

__all__ = ["MCPClient", "SecurityManager", "SecurityViolation", "LakeraClient"] 