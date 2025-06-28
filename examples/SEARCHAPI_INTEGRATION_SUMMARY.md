# SearchAPI MCP Server Integration Summary

This document provides a complete guide on how to use the [searchapi-mcp-server](https://github.com/mrgoonie/searchapi-mcp-server) with our simple MCP client.

## 🎯 Overview

The searchapi-mcp-server is a TypeScript MCP server that provides three powerful search tools:
- **`search_google`** - Google web search
- **`search_google_images`** - Google image search  
- **`search_youtube`** - YouTube video search

Our simple MCP client can connect to this server and use these tools with full security screening and multi-server management capabilities.

## 📁 Files in This Example

- **`searchapi_integration_demo.py`** - Comprehensive demo showing all features
- **`setup_searchapi_demo.py`** - Automated setup script
- **`test_searchapi_integration.py`** - Test script to verify integration
- **`README_searchapi_integration.md`** - Detailed documentation
- **`SEARCHAPI_INTEGRATION_SUMMARY.md`** - This summary document

## 🚀 Quick Start

### 1. Setup (Choose One)

**Option A: Automated Setup**
```bash
python examples/setup_searchapi_demo.py
```

**Option B: Manual Setup**
```bash
# Clone and setup searchapi-mcp-server
git clone https://github.com/mrgoonie/searchapi-mcp-server.git
cd searchapi-mcp-server
npm install

# Set API key
export SEARCHAPI_API_KEY='your-api-key-here'

# Start server
npm run dev:server
```

### 2. Run the Demo

```bash
# In another terminal
python examples/searchapi_integration_demo.py
```

### 3. Test the Integration

```bash
python examples/test_searchapi_integration.py
```

## 🔧 How It Works

### 1. Server Registration

The searchapi-mcp-server registers its tools using the standard MCP `register` function:

```typescript
// From searchapi-mcp-server/src/tools/searchapi.tool.ts
function register(server: McpServer) {
    server.tool(
        'search_google',
        'Performs a Google search using SearchAPI.site...',
        GoogleSearchToolArgs.shape,
        handleGoogleSearch,
    );
    
    server.tool(
        'search_google_images',
        'Performs a Google image search using SearchAPI.site...',
        GoogleImageSearchToolArgs.shape,
        handleGoogleImageSearch,
    );
    
    server.tool(
        'search_youtube',
        'Performs a YouTube search using SearchAPI.site...',
        YouTubeSearchToolArgs.shape,
        handleYouTubeSearch,
    );
}
```

### 2. Client Connection

Our client connects to the server and discovers these tools:

```python
from simple_mcp_client import MCPClient

# Create client
client = MCPClient("http://localhost:5173")

# Connect and discover tools
client.connect()
response = client.list_tools()

# Tools are automatically discovered and available
tools = response.result['tools']
# Returns: ['search_google', 'search_google_images', 'search_youtube']
```

### 3. Tool Usage

Call any of the available tools:

```python
# Google search
response = client.call_tool("search_google", {
    "query": "Model Context Protocol",
    "limit": 5
})

# YouTube search
response = client.call_tool("search_youtube", {
    "query": "MCP tutorial",
    "maxResults": 3,
    "order": "relevance"
})

# Google image search
response = client.call_tool("search_google_images", {
    "query": "MCP logo",
    "limit": 3
})
```

## 🖥️ Multi-Server Management

Our client supports managing multiple MCP servers simultaneously:

```python
from simple_mcp_client.core.multi_client import MultiMCPClient
from simple_mcp_client.config.server_config import add_server_config

# Add searchapi-mcp-server to persistent configuration
add_server_config(
    name="searchapi",
    url="http://localhost:5173",
    description="Search API tools",
    tags=["search", "api"],
    priority=1
)

# Create multi-server client
client = MultiMCPClient()
client.add_server("http://localhost:5173")

# List all tools across all servers
tools = client.list_tools()

# Call tools with automatic routing
response = client.call_tool("search_google", {
    "query": "MCP tutorial",
    "limit": 3
})
# Automatically routes to the correct server
```

## 🔒 Security Features

All interactions are automatically screened for security threats:

```python
# Security screening is enabled by default
client = MCPClient("http://localhost:5173")

# All tool calls are screened
response = client.call_tool("search_google", {
    "query": "safe search query"
})

# Get security statistics
stats = client.get_security_stats()
print(f"Security violations: {stats['violations_detected']}")
```

## 📋 Tool Specifications

### search_google
```json
{
  "query": "string (required)",
  "apiKey": "string (optional)",
  "limit": "number 1-100 (optional)",
  "offset": "number (optional)",
  "sort": "string (optional)",
  "from_date": "string YYYY-MM-DD (optional)",
  "to_date": "string YYYY-MM-DD (optional)"
}
```

### search_google_images
```json
{
  "query": "string (required)",
  "apiKey": "string (optional)",
  "limit": "number 1-100 (optional)",
  "offset": "number (optional)",
  "sort": "string (optional)",
  "from_date": "string YYYY-MM-DD (optional)",
  "to_date": "string YYYY-MM-DD (optional)"
}
```

### search_youtube
```json
{
  "query": "string (required)",
  "apiKey": "string (optional)",
  "maxResults": "number 1-50 (optional)",
  "pageToken": "string (optional)",
  "order": "enum: date|viewCount|rating|relevance (optional)",
  "publishedAfter": "number (optional)",
  "videoDuration": "enum: short|medium|long|any (optional)"
}
```

## 🎯 CLI Usage

### Single Server Commands
```bash
# Connect and list tools
simple-mcp-client server connect --server-url http://localhost:5173
simple-mcp-client server list-tools --server-url http://localhost:5173

# Call tools
simple-mcp-client server call-tool --server-url http://localhost:5173 \
  --tool-name search_google \
  --arguments '{"query": "MCP tutorial", "limit": 5}'
```

### Multi-Server Commands
```bash
# Add server to configuration
simple-mcp-client multi add-server \
  --name searchapi \
  --url http://localhost:5173 \
  --description "Search API tools" \
  --tags search,api

# List all tools and call with automatic routing
simple-mcp-client multi list-all-tools
simple-mcp-client multi call-tool-multi \
  --tool-name search_google \
  --arguments '{"query": "MCP tutorial", "limit": 3}'
```

## ⚙️ Configuration

The client uses a configuration file at `~/.simple_mcp_client/config.json`:

```json
{
  "servers": [
    {
      "name": "searchapi",
      "url": "http://localhost:5173",
      "description": "Search API tools for Google, YouTube, and image search",
      "enabled": true,
      "timeout": 30,
      "priority": 1,
      "tags": ["search", "api", "google", "youtube"],
      "metadata": {
        "api_key_env": "SEARCHAPI_API_KEY",
        "docs": "https://github.com/mrgoonie/searchapi-mcp-server"
      }
    }
  ],
  "default_timeout": 30,
  "enable_security": true,
  "security_fail_on_violation": true,
  "auto_discover": true
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python examples/test_searchapi_integration.py
```

This tests:
- ✅ Connection to searchapi-mcp-server
- ✅ Tool discovery
- ✅ Tool calls (Google search, YouTube search)
- ✅ Multi-server functionality
- ✅ Configuration management

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure searchapi-mcp-server is running on http://localhost:5173
   - Check server logs for errors

2. **API Key Issues**
   - Verify SEARCHAPI_API_KEY is set correctly
   - Check your SearchAPI.site account

3. **Tool Not Found**
   - Ensure tool names match exactly (case-sensitive)
   - Check that server is properly registered

4. **Security Violations**
   - Review search queries for malicious content
   - Use permissive mode for testing

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
python examples/searchapi_integration_demo.py
```

## 📚 Key Benefits

1. **Easy Integration** - Simple Python API for complex search capabilities
2. **Security First** - Built-in Lakera Guard security screening
3. **Multi-Server Support** - Manage multiple MCP servers simultaneously
4. **Persistent Configuration** - Save server settings for reuse
5. **Automatic Routing** - Tools automatically route to correct servers
6. **Comprehensive Testing** - Full test suite for reliability

## 🎉 What You've Learned

By following this example, you've learned how to:

- Connect to external MCP servers using our client
- Discover and use MCP tools programmatically
- Manage multiple servers with intelligent routing
- Apply security screening to external tool calls
- Configure persistent server settings
- Use both Python API and CLI interfaces
- Test and validate MCP integrations

This pattern can be applied to any MCP server that follows the standard protocol, making our client a powerful tool for building MCP-based applications. 