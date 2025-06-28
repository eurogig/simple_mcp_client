#!/usr/bin/env python3
"""
Basic usage example for the Simple MCP Client.

This example demonstrates how to use the MCP client to connect to a server
and interact with available tools.
"""

import json
import sys
from simple_mcp_client import MCPClient


def main():
    """Main example function."""
    # Example server URL (replace with your actual MCP server)
    server_url = "http://localhost:8000"
    
    print(f"Connecting to MCP server at {server_url}")
    
    try:
        # Create and use the client as a context manager
        with MCPClient(server_url) as client:
            # Test the connection
            if not client.connect():
                print("❌ Failed to connect to MCP server")
                sys.exit(1)
            
            print("✅ Successfully connected to MCP server")
            
            # List available tools
            print("\n📋 Listing available tools...")
            response = client.list_tools()
            
            if response.error:
                print(f"❌ Error listing tools: {response.error}")
                return
            
            tools = response.result.get('tools', [])
            if tools:
                print(f"Found {len(tools)} tool(s):")
                for tool in tools:
                    name = tool.get('name', 'Unknown')
                    description = tool.get('description', 'No description')
                    print(f"  - {name}: {description}")
            else:
                print("No tools available")
            
            # Example: Call a specific tool (if available)
            if tools:
                first_tool = tools[0]
                tool_name = first_tool.get('name')
                
                print(f"\n🔧 Calling tool: {tool_name}")
                
                # Example arguments (adjust based on your tool's requirements)
                arguments = {
                    "input": "Hello from Simple MCP Client!"
                }
                
                try:
                    response = client.call_tool(tool_name, arguments)
                    
                    if response.error:
                        print(f"❌ Error calling tool: {response.error}")
                    else:
                        result = response.result or {}
                        print("✅ Tool executed successfully")
                        print(f"Result: {json.dumps(result, indent=2)}")
                        
                except Exception as e:
                    print(f"❌ Exception while calling tool: {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 