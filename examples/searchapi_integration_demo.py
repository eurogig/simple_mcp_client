#!/usr/bin/env python3
"""
SearchAPI MCP Server Integration Demo

This example demonstrates how to use the searchapi-mcp-server 
(https://github.com/mrgoonie/searchapi-mcp-server) with our simple MCP client.

The searchapi-mcp-server provides three main tools:
- search_google: Perform Google web searches
- search_google_images: Perform Google image searches  
- search_youtube: Perform YouTube video searches

Prerequisites:
1. Install and run the searchapi-mcp-server:
   git clone https://github.com/mrgoonie/searchapi-mcp-server.git
   cd searchapi-mcp-server
   npm install
   npm run dev:server

2. Get a SearchAPI.site API key from https://searchapi.site/profile

3. Set environment variables:
   export SEARCHAPI_API_KEY='your-api-key-here'
   export LAKERA_GUARD_API_KEY='your-lakera-key-here'  # Optional for security
"""

import os
import json
from typing import Dict, Any
from simple_mcp_client import MCPClient
from simple_mcp_client.core.multi_client import MultiMCPClient
from simple_mcp_client.config.server_config import add_server_config, list_server_configs


def print_separator(title: str):
    """Print a formatted separator with title."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_tool_info(tool):
    """Print formatted tool information."""
    print(f"  📋 {tool.name}")
    print(f"     Description: {tool.description}")
    print(f"     Parameters: {json.dumps(tool.parameters, indent=6)}")
    print(f"     Server: {tool.server_url}")
    print()


def demo_single_server_usage():
    """Demonstrate single server usage with searchapi-mcp-server."""
    print_separator("Single Server Usage Demo")
    
    # Create a single server client
    # Assuming searchapi-mcp-server is running on localhost:5173
    client = MCPClient("http://localhost:5173")
    
    try:
        print("🔗 Connecting to searchapi-mcp-server...")
        connected = client.connect()
        if connected:
            print("✅ Connected successfully!")
        else:
            print("❌ Failed to connect")
            return
        
        # List available tools
        print("\n📋 Available tools:")
        response = client.list_tools()
        if response.result and 'tools' in response.result:
            tools = response.result['tools']
            for tool_data in tools:
                print(f"  📋 {tool_data.get('name', 'Unknown')}")
                print(f"     Description: {tool_data.get('description', 'No description')}")
                print(f"     Parameters: {json.dumps(tool_data.get('parameters', {}), indent=6)}")
                print()
        
        # Example 1: Google Search
        print("🔍 Performing Google search...")
        search_args = {
            "query": "Model Context Protocol MCP",
            "limit": 5
        }
        
        response = client.call_tool("search_google", search_args)
        print("✅ Google search results:")
        if response.result and 'content' in response.result:
            print(response.result['content'])
        else:
            print("No results or error occurred")
        
        # Example 2: YouTube Search
        print("\n🎥 Performing YouTube search...")
        youtube_args = {
            "query": "Model Context Protocol tutorial",
            "maxResults": 3,
            "order": "relevance"
        }
        
        response = client.call_tool("search_youtube", youtube_args)
        print("✅ YouTube search results:")
        if response.result and 'content' in response.result:
            print(response.result['content'])
        else:
            print("No results or error occurred")
        
        # Example 3: Google Image Search
        print("\n🖼️ Performing Google image search...")
        image_args = {
            "query": "Model Context Protocol logo",
            "limit": 3
        }
        
        response = client.call_tool("search_google_images", image_args)
        print("✅ Google image search results:")
        if response.result and 'content' in response.result:
            print(response.result['content'])
        else:
            print("No results or error occurred")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


def demo_multi_server_usage():
    """Demonstrate multi-server usage with searchapi-mcp-server and other servers."""
    print_separator("Multi-Server Usage Demo")
    
    # Create multi-server client
    client = MultiMCPClient()
    
    try:
        # Add searchapi-mcp-server to configuration
        print("⚙️ Adding searchapi-mcp-server to configuration...")
        add_server_config(
            name="searchapi",
            url="http://localhost:5173",
            description="Search API tools for Google, YouTube, and image search",
            tags=["search", "api", "google", "youtube"],
            priority=1
        )
        
        # Add some hypothetical other servers for demonstration
        add_server_config(
            name="math-server",
            url="http://localhost:8001",
            description="Mathematical operations and calculations",
            tags=["math", "calculations"],
            priority=2
        )
        
        add_server_config(
            name="file-server", 
            url="http://localhost:8002",
            description="File operations and management",
            tags=["files", "io"],
            priority=3
        )
        
        # List configured servers
        print("\n📋 Configured servers:")
        servers = list_server_configs()
        for server in servers:
            print(f"  🖥️ {server.name}: {server.url}")
            print(f"     Description: {server.description}")
            print(f"     Tags: {', '.join(server.tags)}")
            print(f"     Priority: {server.priority}")
            print()
        
        # Add servers to client (only searchapi will be available)
        print("🔗 Connecting to configured servers...")
        success = client.add_server("http://localhost:5173")  # searchapi-mcp-server
        if not success:
            print("❌ Failed to add searchapi-mcp-server")
            return
        
        # List all available tools across servers
        print("\n📋 All available tools:")
        tools = client.list_tools()
        for tool in tools:
            print_tool_info(tool)
        
        # Search for specific tools
        print("🔍 Searching for search-related tools...")
        search_tools = client.search_tools("search")
        print(f"Found {len(search_tools)} search-related tools:")
        for tool in search_tools:
            print(f"  - {tool.name} (on {tool.server_url})")
        
        # Call tools without knowing which server they're on
        print("\n🎯 Calling tools with automatic routing...")
        
        # This will automatically route to searchapi-mcp-server
        response = client.call_tool("search_google", {
            "query": "MCP Model Context Protocol",
            "limit": 3
        })
        print("✅ Google search completed via automatic routing")
        if response.result and 'content' in response.result:
            print(response.result['content'])
        else:
            print("No results or error occurred")
        
        # Get statistics
        stats = client.get_stats()
        print(f"\n📊 Client Statistics:")
        print(f"  Total servers: {stats['total_servers']}")
        print(f"  Total tools: {stats['total_tools']}")
        print(f"  Connected servers: {stats['connected_servers']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


def demo_cli_equivalent():
    """Show the CLI commands equivalent to the Python API usage."""
    print_separator("CLI Equivalent Commands")
    
    print("Here are the CLI commands equivalent to the Python API usage:")
    print()
    
    print("🔗 Single Server Commands:")
    print("  # Connect to searchapi-mcp-server")
    print("  simple-mcp-client server connect --server-url http://localhost:5173")
    print()
    print("  # List available tools")
    print("  simple-mcp-client server list-tools --server-url http://localhost:5173")
    print()
    print("  # Perform Google search")
    print("  simple-mcp-client server call-tool --server-url http://localhost:5173 \\")
    print("    --tool-name search_google \\")
    print("    --arguments '{\"query\": \"Model Context Protocol\", \"limit\": 5}'")
    print()
    
    print("🖥️ Multi-Server Commands:")
    print("  # Add searchapi-mcp-server to configuration")
    print("  simple-mcp-client multi add-server \\")
    print("    --name searchapi \\")
    print("    --url http://localhost:5173 \\")
    print("    --description \"Search API tools\" \\")
    print("    --tags search,api,google,youtube")
    print()
    print("  # List all configured servers")
    print("  simple-mcp-client multi list-servers")
    print()
    print("  # List all tools across all servers")
    print("  simple-mcp-client multi list-all-tools")
    print()
    print("  # Call any tool (automatic routing)")
    print("  simple-mcp-client multi call-tool-multi \\")
    print("    --tool-name search_google \\")
    print("    --arguments '{\"query\": \"MCP tutorial\", \"limit\": 3}'")
    print()
    
    print("🔒 Security Screening:")
    print("  # Screen content directly")
    print("  simple-mcp-client screen --content \"Hello, how are you today?\"")
    print()
    print("  # Disable security (not recommended)")
    print("  simple-mcp-client server connect --server-url http://localhost:5173 --disable-security")


def demo_configuration_file():
    """Show the configuration file structure."""
    print_separator("Configuration File Structure")
    
    config_example = {
        "servers": [
            {
                "name": "searchapi",
                "url": "http://localhost:5173",
                "description": "Search API tools for Google, YouTube, and image search",
                "enabled": True,
                "timeout": 30,
                "priority": 1,
                "tags": ["search", "api", "google", "youtube"],
                "metadata": {
                    "api_key_env": "SEARCHAPI_API_KEY",
                    "docs": "https://github.com/mrgoonie/searchapi-mcp-server"
                }
            },
            {
                "name": "math-server",
                "url": "http://localhost:8001", 
                "description": "Mathematical operations and calculations",
                "enabled": True,
                "timeout": 30,
                "priority": 2,
                "tags": ["math", "calculations"],
                "metadata": {}
            }
        ],
        "default_timeout": 30,
        "enable_security": True,
        "security_fail_on_violation": True,
        "auto_discover": True,
        "refresh_interval": None
    }
    
    print("Configuration file location: ~/.simple_mcp_client/config.json")
    print()
    print("Example configuration:")
    print(json.dumps(config_example, indent=2))


def main():
    """Main demo function."""
    print("🚀 SearchAPI MCP Server Integration Demo")
    print("This demo shows how to use the searchapi-mcp-server with our simple MCP client")
    print()
    print("Prerequisites:")
    print("1. searchapi-mcp-server running on http://localhost:5173")
    print("2. SEARCHAPI_API_KEY environment variable set")
    print("3. LAKERA_GUARD_API_KEY environment variable set (optional)")
    print()
    
    # Check environment variables
    searchapi_key = os.getenv("SEARCHAPI_API_KEY")
    lakera_key = os.getenv("LAKERA_GUARD_API_KEY")
    
    print("Environment Check:")
    print(f"  SEARCHAPI_API_KEY: {'✅ Set' if searchapi_key else '❌ Not set'}")
    print(f"  LAKERA_GUARD_API_KEY: {'✅ Set' if lakera_key else '⚠️ Not set (security disabled)'}")
    print()
    
    if not searchapi_key:
        print("⚠️ Warning: SEARCHAPI_API_KEY not set. Some examples may fail.")
        print("   Get your API key from: https://searchapi.site/profile")
        print()
    
    # Run demos
    try:
        demo_single_server_usage()
        demo_multi_server_usage()
        demo_cli_equivalent()
        demo_configuration_file()
        
        print_separator("Demo Complete")
        print("✅ All demos completed successfully!")
        print()
        print("Next steps:")
        print("1. Set up your SearchAPI.site API key")
        print("2. Start the searchapi-mcp-server")
        print("3. Run this demo again to see it in action")
        print("4. Explore the CLI commands for interactive usage")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure searchapi-mcp-server is running on http://localhost:5173")
        print("2. Check that your API keys are set correctly")
        print("3. Verify network connectivity")


if __name__ == "__main__":
    main() 