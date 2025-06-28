# SearchAPI MCP Server Integration

This example demonstrates how to use the [searchapi-mcp-server](https://github.com/mrgoonie/searchapi-mcp-server) with our simple MCP client. The searchapi-mcp-server provides powerful search capabilities through SearchAPI.site, including Google web search, Google image search, and YouTube search.

## 🎯 What You'll Learn

- How to connect to an MCP server using our client
- How to discover and use MCP tools
- How to manage multiple MCP servers
- How to use security screening with external tools
- How to configure persistent server settings

## 🛠️ Prerequisites

1. **Node.js and npm** - Required for the searchapi-mcp-server
2. **Git** - For cloning the searchapi-mcp-server repository
3. **SearchAPI.site API key** - Get one at [https://searchapi.site/profile](https://searchapi.site/profile)
4. **Lakera Guard API key** (optional) - For security screening

## 🚀 Quick Setup

### 1. Automated Setup

Run our setup script to automatically configure everything:

```bash
python examples/setup_searchapi_demo.py
```

This script will:
- Check for required dependencies (Node.js, npm, git)
- Clone the searchapi-mcp-server repository
- Install dependencies
- Create configuration files
- Guide you through the remaining setup steps

### 2. Manual Setup

If you prefer to set up manually:

```bash
# Clone the searchapi-mcp-server
git clone https://github.com/mrgoonie/searchapi-mcp-server.git
cd searchapi-mcp-server

# Install dependencies
npm install

# Set your API key
export SEARCHAPI_API_KEY='your-api-key-here'

# Start the server
npm run dev:server
```

## 📋 Available Tools

The searchapi-mcp-server provides three main tools:

### 1. `search_google` - Google Web Search
```json
{
  "query": "Model Context Protocol",
  "limit": 5,
  "apiKey": "your-api-key"
}
```

### 2. `search_google_images` - Google Image Search
```json
{
  "query": "MCP logo",
  "limit": 3,
  "apiKey": "your-api-key"
}
```

### 3. `search_youtube` - YouTube Search
```json
{
  "query": "MCP tutorial",
  "maxResults": 3,
  "order": "relevance",
  "apiKey": "your-api-key"
}
```

## 🔧 Usage Examples

### Single Server Usage

```python
from simple_mcp_client import MCPClient

# Create client
client = MCPClient("http://localhost:5173")

# Connect and list tools
client.connect()
tools = client.list_tools()

# Perform Google search
response = client.call_tool("search_google", {
    "query": "Model Context Protocol MCP",
    "limit": 5
})
print(response.result['content'])
```

### Multi-Server Usage

```python
from simple_mcp_client.core.multi_client import MultiMCPClient
from simple_mcp_client.config.server_config import add_server_config

# Add server to configuration
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

# List all tools
tools = client.list_tools()

# Call tools with automatic routing
response = client.call_tool("search_google", {
    "query": "MCP tutorial",
    "limit": 3
})
```

### CLI Usage

```bash
# Single server commands
simple-mcp-client server connect --server-url http://localhost:5173
simple-mcp-client server list-tools --server-url http://localhost:5173
simple-mcp-client server call-tool --server-url http://localhost:5173 \
  --tool-name search_google \
  --arguments '{"query": "MCP tutorial", "limit": 5}'

# Multi-server commands
simple-mcp-client multi add-server \
  --name searchapi \
  --url http://localhost:5173 \
  --description "Search API tools" \
  --tags search,api
simple-mcp-client multi list-all-tools
simple-mcp-client multi call-tool-multi \
  --tool-name search_google \
  --arguments '{"query": "MCP tutorial", "limit": 3}'
```

## 🔒 Security Features

Our client includes security screening powered by Lakera Guard:

```python
# Security screening is enabled by default
client = MCPClient("http://localhost:5173")

# All tool calls are automatically screened
response = client.call_tool("search_google", {
    "query": "safe search query"
})

# Get security statistics
stats = client.get_security_stats()
print(f"Security violations: {stats['violations_detected']}")
```

### Security Configuration

```python
from simple_mcp_client import SecurityManager

# Create security manager with custom settings
security_manager = SecurityManager(
    enable_tool_screening=True,
    enable_interaction_screening=True,
    fail_on_violation=True  # Strict mode
)

client = MCPClient(
    "http://localhost:5173",
    security_manager=security_manager
)
```

## ⚙️ Configuration Management

The client supports persistent configuration:

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

## 🧪 Running the Demo

1. **Start the searchapi-mcp-server:**
   ```bash
   cd searchapi-mcp-server
   npm run dev:server
   ```

2. **In another terminal, run the demo:**
   ```bash
   python examples/searchapi_integration_demo.py
   ```

3. **Or use the setup script:**
   ```bash
   python examples/setup_searchapi_demo.py start
   ```

## 🔍 Tool Discovery

The demo shows how to discover and explore available tools:

```python
# List all tools
tools = client.list_tools()
for tool in tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Parameters: {tool.parameters}")

# Search for specific tools
search_tools = client.search_tools("search")
youtube_tools = client.search_tools("youtube")
```

## 🎯 Advanced Features

### Tool Routing
The multi-server client automatically routes tool calls to the correct server:

```python
# This automatically finds and calls the tool on the right server
response = client.call_tool("search_google", {"query": "MCP"})
```

### Server Prioritization
Configure server priorities for tool selection:

```python
add_server_config(
    name="primary-search",
    url="http://localhost:5173",
    priority=1  # Higher priority
)

add_server_config(
    name="backup-search", 
    url="http://localhost:5174",
    priority=2  # Lower priority
)
```

### Error Handling
The client provides comprehensive error handling:

```python
try:
    response = client.call_tool("search_google", {"query": "test"})
    print(response.result['content'])
except SecurityViolation as e:
    print(f"Security violation: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Make sure searchapi-mcp-server is running on http://localhost:5173
   - Check that the server started without errors

2. **API Key Issues**
   - Verify SEARCHAPI_API_KEY is set correctly
   - Check your SearchAPI.site account for valid API key

3. **Security Violations**
   - Review the search query for potentially malicious content
   - Consider using permissive mode for testing

4. **Tool Not Found**
   - Ensure the tool name matches exactly (case-sensitive)
   - Check that the server is properly registered

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
python examples/searchapi_integration_demo.py
```

### Server Logs

Check the searchapi-mcp-server logs for detailed information:

```bash
cd searchapi-mcp-server
DEBUG=true npm run dev:server
```

## 📚 Additional Resources

- [SearchAPI MCP Server Documentation](https://github.com/mrgoonie/searchapi-mcp-server)
- [SearchAPI.site API Documentation](https://searchapi.site/docs)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Lakera Guard Security](https://lakera.ai)

## 🤝 Contributing

Found an issue or have a suggestion? Please:

1. Check the existing issues
2. Create a new issue with detailed information
3. Submit a pull request with your improvements

## 📄 License

This example is part of the simple-mcp-client project and follows the same license terms. 