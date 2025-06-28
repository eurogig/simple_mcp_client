#!/usr/bin/env python3
"""
Multi-server MCP client demonstration.

This example demonstrates how to use the multi-server MCP client
to manage multiple servers and intelligently route tool requests.
"""

import json
import os
import sys
from simple_mcp_client import MultiMCPClient, SecurityManager


def demo_server_management():
    """Demonstrate server management functionality."""
    print("🖥️  Server Management Demo")
    print("=" * 50)
    
    # Create multi-server client
    with MultiMCPClient() as client:
        # Add multiple servers (example URLs - replace with real ones)
        servers = [
            "http://localhost:8001",  # Math tools server
            "http://localhost:8002",  # File operations server
            "http://localhost:8003",  # Database tools server
        ]
        
        print("Adding servers...")
        for i, server_url in enumerate(servers):
            if client.add_server(server_url):
                print(f"✅ Added server {i+1}: {server_url}")
            else:
                print(f"❌ Failed to add server {i+1}: {server_url}")
        
        # Show server information
        print(f"\n📊 Server Information:")
        server_info = client.get_server_info()
        for url, info in server_info.items():
            print(f"  - {url}: {info['tool_count']} tools, connected: {info['connected']}")
        
        # Show all available tools
        print(f"\n🔧 Available Tools:")
        tools = client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
            print(f"    Server: {tool.server_url}")


def demo_tool_routing():
    """Demonstrate intelligent tool routing."""
    print("\n🔄 Tool Routing Demo")
    print("=" * 50)
    
    with MultiMCPClient() as client:
        # Add servers (replace with real URLs)
        client.add_server("http://localhost:8001")
        client.add_server("http://localhost:8002")
        
        # Search for tools
        print("Searching for calculator tools...")
        calculator_tools = client.search_tools("calculator")
        print(f"Found {len(calculator_tools)} calculator tools:")
        for tool in calculator_tools:
            print(f"  - {tool.name} on {tool.server_url}")
        
        # Call a specific tool (if available)
        tool_name = "calculator"
        if client.find_tool(tool_name):
            print(f"\nCalling {tool_name}...")
            try:
                response = client.call_tool(tool_name, {
                    "operation": "add",
                    "numbers": [1, 2, 3]
                })
                print(f"✅ Tool response: {response.result}")
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
        else:
            print(f"Tool '{tool_name}' not found")


def demo_configuration_management():
    """Demonstrate configuration management."""
    print("\n⚙️  Configuration Management Demo")
    print("=" * 50)
    
    from simple_mcp_client.config import (
        add_server_config,
        list_server_configs,
        remove_server_config
    )
    
    # Add servers to configuration
    print("Adding servers to configuration...")
    
    add_server_config(
        name="math-server",
        url="http://localhost:8001",
        description="Server providing mathematical operations",
        tags=["math", "calculations"],
        priority=1
    )
    
    add_server_config(
        name="file-server",
        url="http://localhost:8002",
        description="Server providing file operations",
        tags=["files", "io"],
        priority=2
    )
    
    # List configured servers
    print("\nConfigured servers:")
    servers = list_server_configs()
    for server in servers:
        print(f"  - {server.name}: {server.url}")
        print(f"    Description: {server.description}")
        print(f"    Tags: {', '.join(server.tags)}")
        print(f"    Priority: {server.priority}")


def demo_security_integration():
    """Demonstrate security integration with multi-server client."""
    print("\n🔒 Security Integration Demo")
    print("=" * 50)
    
    try:
        # Create security manager
        security_manager = SecurityManager()
        
        # Create multi-server client with security
        with MultiMCPClient(security_manager=security_manager) as client:
            # Add servers (replace with real URLs)
            client.add_server("http://localhost:8001")
            client.add_server("http://localhost:8002")
            
            # Show security statistics
            stats = client.get_stats()
            print(f"📊 Client Statistics: {stats}")
            
            # List tools (will be screened for security)
            tools = client.list_tools()
            print(f"Found {len(tools)} safe tools across all servers")
            
    except Exception as e:
        print(f"❌ Security demo error: {e}")
        print("   Make sure LAKERA_GUARD_API_KEY is set for security features")


def demo_advanced_features():
    """Demonstrate advanced multi-server features."""
    print("\n🚀 Advanced Features Demo")
    print("=" * 50)
    
    with MultiMCPClient() as client:
        # Add servers
        client.add_server("http://localhost:8001")
        client.add_server("http://localhost:8002")
        
        # Tool discovery and management
        print("Tool discovery across servers...")
        tools = client.list_tools()
        
        # Group tools by server
        tools_by_server = {}
        for tool in tools:
            if tool.server_url not in tools_by_server:
                tools_by_server[tool.server_url] = []
            tools_by_server[tool.server_url].append(tool)
        
        print("Tools by server:")
        for server_url, server_tools in tools_by_server.items():
            print(f"  {server_url}:")
            for tool in server_tools:
                print(f"    - {tool.name}: {tool.description}")
        
        # Search functionality
        print("\nSearching for tools...")
        search_terms = ["calc", "file", "db"]
        for term in search_terms:
            matches = client.search_tools(term)
            print(f"  '{term}': {len(matches)} matches")
            for tool in matches:
                print(f"    - {tool.name} on {tool.server_url}")


def main():
    """Main demonstration function."""
    print("🚀 Multi-Server MCP Client Demo")
    print("=" * 60)
    
    # Check if we have any servers configured
    from simple_mcp_client.config import list_server_configs
    servers = list_server_configs()
    
    if not servers:
        print("⚠️  No servers configured")
        print("   This demo uses example server URLs")
        print("   In a real scenario, you would:")
        print("   1. Add servers using: simple-mcp-client multi add-server")
        print("   2. Configure them with proper URLs")
        print("   3. Enable them for use")
        print()
    
    # Run demonstrations
    demo_server_management()
    demo_tool_routing()
    demo_configuration_management()
    demo_security_integration()
    demo_advanced_features()
    
    print("\n🎉 Multi-server demonstration completed!")
    print("\n💡 Key Benefits:")
    print("   - Manage multiple MCP servers from one client")
    print("   - Automatic tool discovery and routing")
    print("   - Intelligent tool selection")
    print("   - Unified security screening")
    print("   - Configuration persistence")
    print("\n🔧 CLI Commands:")
    print("   - simple-mcp-client multi add-server --name math --url http://localhost:8001")
    print("   - simple-mcp-client multi list-servers")
    print("   - simple-mcp-client multi list-all-tools")
    print("   - simple-mcp-client multi call-tool-multi --tool-name calculator")


if __name__ == "__main__":
    main() 