#!/usr/bin/env python3
"""
Test script for SearchAPI MCP Server Integration

This script tests the integration between our simple MCP client and the searchapi-mcp-server.
It can be run to verify that everything is working correctly.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simple_mcp_client import MCPClient
from simple_mcp_client.core.multi_client import MultiMCPClient
from simple_mcp_client.config.server_config import add_server_config, list_server_configs


def test_connection():
    """Test basic connection to searchapi-mcp-server."""
    print("🔗 Testing connection to searchapi-mcp-server...")
    
    client = MCPClient("http://localhost:5173")
    
    try:
        connected = client.connect()
        if connected:
            print("✅ Connection successful!")
            return True
        else:
            print("❌ Connection failed!")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    finally:
        client.close()


def test_tool_discovery():
    """Test tool discovery from searchapi-mcp-server."""
    print("\n📋 Testing tool discovery...")
    
    client = MCPClient("http://localhost:5173")
    
    try:
        client.connect()
        response = client.list_tools()
        
        if response.result and 'tools' in response.result:
            tools = response.result['tools']
            print(f"✅ Found {len(tools)} tools:")
            
            expected_tools = ['search_google', 'search_google_images', 'search_youtube']
            found_tools = [tool.get('name') for tool in tools]
            
            for expected in expected_tools:
                if expected in found_tools:
                    print(f"  ✅ {expected}")
                else:
                    print(f"  ❌ {expected} (not found)")
            
            return all(expected in found_tools for expected in expected_tools)
        else:
            print("❌ No tools found or invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Tool discovery error: {e}")
        return False
    finally:
        client.close()


def test_tool_calls():
    """Test calling tools from searchapi-mcp-server."""
    print("\n🔍 Testing tool calls...")
    
    client = MCPClient("http://localhost:5173")
    
    try:
        client.connect()
        
        # Test Google search
        print("  Testing search_google...")
        response = client.call_tool("search_google", {
            "query": "Model Context Protocol",
            "limit": 1
        })
        
        if response.result and 'content' in response.result:
            print("  ✅ search_google call successful")
        else:
            print("  ❌ search_google call failed")
            return False
        
        # Test YouTube search
        print("  Testing search_youtube...")
        response = client.call_tool("search_youtube", {
            "query": "MCP tutorial",
            "maxResults": 1
        })
        
        if response.result and 'content' in response.result:
            print("  ✅ search_youtube call successful")
        else:
            print("  ❌ search_youtube call failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tool call error: {e}")
        return False
    finally:
        client.close()


def test_multi_server():
    """Test multi-server functionality."""
    print("\n🖥️ Testing multi-server functionality...")
    
    # Add server to configuration
    add_server_config(
        name="test-searchapi",
        url="http://localhost:5173",
        description="Test SearchAPI server",
        tags=["test", "search"],
        priority=1
    )
    
    # Create multi-server client
    client = MultiMCPClient()
    
    try:
        # Add server
        success = client.add_server("http://localhost:5173")
        if not success:
            print("❌ Failed to add server to multi-client")
            return False
        
        # List tools
        tools = client.list_tools()
        print(f"✅ Found {len(tools)} tools in multi-server mode")
        
        # Search for tools
        search_tools = client.search_tools("search")
        print(f"✅ Found {len(search_tools)} search-related tools")
        
        # Test tool routing
        response = client.call_tool("search_google", {
            "query": "MCP test",
            "limit": 1
        })
        
        if response.result and 'content' in response.result:
            print("✅ Multi-server tool routing successful")
            return True
        else:
            print("❌ Multi-server tool routing failed")
            return False
            
    except Exception as e:
        print(f"❌ Multi-server error: {e}")
        return False
    finally:
        client.close()


def test_configuration():
    """Test configuration management."""
    print("\n⚙️ Testing configuration management...")
    
    try:
        # List configured servers
        servers = list_server_configs()
        print(f"✅ Found {len(servers)} configured servers")
        
        # Check for our test server
        test_server = None
        for server in servers:
            if server.name == "test-searchapi":
                test_server = server
                break
        
        if test_server:
            print(f"✅ Test server found: {test_server.name}")
            print(f"  URL: {test_server.url}")
            print(f"  Description: {test_server.description}")
            print(f"  Tags: {', '.join(test_server.tags)}")
            return True
        else:
            print("❌ Test server not found in configuration")
            return False
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 SearchAPI MCP Server Integration Tests")
    print("=" * 50)
    
    # Check environment
    searchapi_key = os.getenv("SEARCHAPI_API_KEY")
    if not searchapi_key:
        print("⚠️ SEARCHAPI_API_KEY not set. Some tests may fail.")
        print("   Set it with: export SEARCHAPI_API_KEY='your-api-key'")
    
    # Run tests
    tests = [
        ("Connection", test_connection),
        ("Tool Discovery", test_tool_discovery),
        ("Tool Calls", test_tool_calls),
        ("Multi-Server", test_multi_server),
        ("Configuration", test_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 