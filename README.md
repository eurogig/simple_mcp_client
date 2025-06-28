# Simple MCP Client

A simple and lightweight client implementation for the Model Context Protocol (MCP) with integrated security screening using [Lakera Guard](https://docs.lakera.ai/docs/api) and multi-server management capabilities.

## Features

- Easy-to-use MCP client implementation
- **🔒 Integrated security screening with Lakera Guard**
- **🛡️ Tool registration security validation**
- **🔄 Real-time server interaction monitoring**
- **🖥️ Multi-server management and tool routing**
- **⚙️ Persistent configuration management**
- **🔍 Intelligent tool discovery and search**
- Command-line interface for quick interactions
- Extensible architecture for custom integrations
- Comprehensive test coverage
- Modern Python packaging with `pyproject.toml`

## Security Features

This client includes comprehensive security screening powered by Lakera Guard to ensure safe interactions with MCP servers:

### 🔍 Content Screening
- **Tool Descriptions**: Automatically screens tool descriptions during registration
- **Server Interactions**: Monitors all requests and responses for security threats
- **Threat Detection**: Identifies prompt injection, jailbreaking, and other malicious content

### 🛡️ Security Configurations
- **Strict Mode**: Fail on any security violation (default)
- **Permissive Mode**: Log violations but continue execution
- **Minimal Mode**: Screen only server interactions
- **Disabled**: No security screening (not recommended for production)

### 📊 Security Monitoring
- Real-time security statistics
- Detailed threat categorization
- Comprehensive logging of security events

## Multi-Server Features

The client supports managing multiple MCP servers with intelligent tool routing:

### 🖥️ Server Management
- **Multiple Server Support**: Connect to and manage multiple MCP servers simultaneously
- **Automatic Tool Discovery**: Discover tools across all connected servers
- **Intelligent Routing**: Automatically route tool calls to the correct server
- **Server Prioritization**: Configure server priorities for tool selection

### ⚙️ Configuration Management
- **Persistent Configuration**: Save server configurations to `~/.simple_mcp_client/config.json`
- **Server Metadata**: Add descriptions, tags, and priorities to servers
- **Environment Support**: Different configurations for different environments
- **Import/Export**: Share configurations across teams

### 🔍 Tool Discovery & Search
- **Cross-Server Search**: Search for tools by name or description across all servers
- **Tool Categorization**: Organize tools by server, tags, and functionality
- **Real-time Updates**: Refresh tool lists when servers change

## Installation

### From PyPI (when published)

```bash
pip install simple-mcp-client
```

### From source

```bash
git clone https://github.com/yourusername/simple_mcp_client.git
cd simple_mcp_client
pip install -e .
```

### Security Setup

To enable security features, you need a Lakera Guard API key:

1. Sign up at [Lakera](https://lakera.ai)
2. Get your API key from the dashboard
3. Set the environment variable:
   ```bash
   export LAKERA_GUARD_API_KEY='your-api-key-here'
   ```

## Quick Start

### Single Server Usage

```bash
# Basic usage with security enabled
simple-mcp-client --help

# Connect to an MCP server with security screening
simple-mcp-client server connect --server-url http://localhost:8000

# List tools with security filtering
simple-mcp-client server list-tools --server-url http://localhost:8000

# Call a tool with security monitoring
simple-mcp-client server call-tool --server-url http://localhost:8000 --tool-name calculator --arguments '{"operation": "add", "numbers": [1, 2]}'

# Screen content directly
simple-mcp-client screen --content "Hello, how are you today?"

# Disable security (not recommended)
simple-mcp-client server connect --server-url http://localhost:8000 --disable-security
```

### Multi-Server Usage

```bash
# Add servers to configuration
simple-mcp-client multi add-server --name math --url http://localhost:8001 --description "Mathematical operations" --tags math,calculations
simple-mcp-client multi add-server --name files --url http://localhost:8002 --description "File operations" --tags files,io
simple-mcp-client multi add-server --name database --url http://localhost:8003 --description "Database tools" --tags db,storage

# List all configured servers
simple-mcp-client multi list-servers

# List all tools across all servers
simple-mcp-client multi list-all-tools

# Call any tool (client routes to correct server automatically)
simple-mcp-client multi call-tool-multi --tool-name calculator --arguments '{"operation": "add", "numbers": [1, 2, 3]}'

# Remove a server
simple-mcp-client multi remove-server --name math
```

### Python API

#### Single Server Client

```python
from simple_mcp_client import MCPClient, SecurityManager, LakeraClient

# Create a client with security enabled (default)
client = MCPClient("http://localhost:8000")

# Connect to the server
client.connect()

# Send a request (automatically screened for security)
response = client.send_request("tools/list")
print(response)

# Get security statistics
stats = client.get_security_stats()
print(f"Security stats: {stats}")

# Direct Lakera Guard usage
with LakeraClient() as lakera:
    result = lakera.screen_content("Hello, world!")
    print(f"Content safe: {not result.flagged}")
```

#### Multi-Server Client

```python
from simple_mcp_client import MultiMCPClient, SecurityManager

# Create multi-server client
client = MultiMCPClient()

# Add multiple servers
client.add_server("http://localhost:8001")  # Math tools
client.add_server("http://localhost:8002")  # File operations
client.add_server("http://localhost:8003")  # Database tools

# List all available tools across all servers
tools = client.list_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description} (on {tool.server_url})")

# Search for specific tools
calculator_tools = client.search_tools("calculator")
file_tools = client.search_tools("file")

# Call any tool (client routes automatically)
response = client.call_tool("calculator", {"operation": "add", "numbers": [1, 2, 3]})
print(response.result)

# Get statistics
stats = client.get_stats()
print(f"Total servers: {stats['total_servers']}, Total tools: {stats['total_tools']}")
```

### Configuration Management

```python
from simple_mcp_client.config import add_server_config, list_server_configs, load_config

# Add servers to persistent configuration
add_server_config(
    name="math-server",
    url="http://localhost:8001",
    description="Mathematical operations",
    tags=["math", "calculations"],
    priority=1
)

# List all configured servers
servers = list_server_configs()
for server in servers:
    print(f"{server.name}: {server.url}")

# Load configuration
config = load_config()
print(f"Configured servers: {len(config.servers)}")
```

### Security Manager

```python
from simple_mcp_client import SecurityManager

# Create security manager with custom configuration
security_manager = SecurityManager(
    enable_tool_screening=True,
    enable_interaction_screening=True,
    fail_on_violation=True  # Strict mode
)

# Screen tool registration
try:
    is_safe = security_manager.screen_tool_registration(
        "calculator",
        "A simple calculator tool",
        {"operation": "string", "numbers": "array"}
    )
    print(f"Tool is safe: {is_safe}")
except SecurityViolation as e:
    print(f"Security violation: {e}")

# Screen server interaction
is_safe = security_manager.screen_server_interaction(
    "tools/call",
    {"name": "calculator", "arguments": {"operation": "add", "numbers": [1, 2]}}
)
print(f"Interaction is safe: {is_safe}")
```

## Configuration File

The client uses a configuration file at `~/.simple_mcp_client/config.json`:

```json
{
  "servers": [
    {
      "name": "math-server",
      "url": "http://localhost:8001",
      "description": "Mathematical operations",
      "enabled": true,
      "timeout": 30,
      "priority": 1,
      "tags": ["math", "calculations"],
      "metadata": {}
    },
    {
      "name": "file-server",
      "url": "http://localhost:8002",
      "description": "File operations",
      "enabled": true,
      "timeout": 30,
      "priority": 2,
      "tags": ["files", "io"],
      "metadata": {}
    }
  ],
  "default_timeout": 30,
  "enable_security": true,
  "security_fail_on_violation": true,
  "auto_discover": true,
  "refresh_interval": null
}
```

## Security Examples

### Tool Registration Screening

When tools register with an MCP server, their descriptions are automatically screened:

```python
# This tool would be flagged as potentially unsafe
unsafe_tool = {
    "name": "system_exec",
    "description": "Execute system commands with elevated privileges",
    "parameters": {"command": "string"}
}

# The security manager will detect this and either:
# - Raise SecurityViolation (strict mode)
# - Return False (permissive mode)
# - Log the violation
```

### Server Interaction Monitoring

All server interactions are monitored for security threats:

```python
# This request would be screened
response = client.send_request("tools/call", {
    "name": "calculator",
    "arguments": {
        "operation": "add",
        "numbers": [1, 2]
    }
})

# The response is also screened for malicious content
# If threats are detected, SecurityViolation is raised
```

### Content Screening

Direct content screening is available:

```python
from simple_mcp_client import LakeraClient

with LakeraClient() as client:
    # Screen any content
    result = client.screen_content("Hello, world!")
    
    if result.flagged:
        print(f"Content flagged: {result.categories}")
        print(f"Threat scores: {result.category_scores}")
    else:
        print("Content appears safe")
```

## Multi-Server Examples

### Tool Discovery Across Servers

```python
from simple_mcp_client import MultiMCPClient

client = MultiMCPClient()

# Add servers
client.add_server("http://math-server:8001")
client.add_server("http://file-server:8002")
client.add_server("http://db-server:8003")

# Discover all tools
tools = client.list_tools()
print(f"Found {len(tools)} tools across {len(client.servers)} servers")

# Group tools by server
tools_by_server = {}
for tool in tools:
    if tool.server_url not in tools_by_server:
        tools_by_server[tool.server_url] = []
    tools_by_server[tool.server_url].append(tool)

for server_url, server_tools in tools_by_server.items():
    print(f"\n{server_url}:")
    for tool in server_tools:
        print(f"  - {tool.name}: {tool.description}")
```

### Intelligent Tool Routing

```python
# Call tools without knowing which server they're on
response = client.call_tool("calculate_integral", {
    "function": "x^2",
    "bounds": [0, 1]
})
# Automatically routes to math-server

response = client.call_tool("read_file", {
    "path": "/data/example.txt"
})
# Automatically routes to file-server

response = client.call_tool("query_database", {
    "sql": "SELECT * FROM users"
})
# Automatically routes to db-server
```

### Tool Search and Selection

```python
# Search for tools by functionality
calculator_tools = client.search_tools("calculator")
file_tools = client.search_tools("file")
db_tools = client.search_tools("database")

# Find specific tool
tool = client.find_tool("calculator")
if tool:
    print(f"Calculator found on: {tool.server_url}")
    print(f"Parameters: {tool.parameters}")
```

## Development

### Setup Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/simple_mcp_client.git
   cd simple_mcp_client
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up Lakera API key for testing:
   ```bash
   export LAKERA_GUARD_API_KEY='your-test-api-key'
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/simple_mcp_client

# Run security tests specifically
pytest tests/test_security.py

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html
```

## Security Configuration

### Environment Variables

- `LAKERA_GUARD_API_KEY`: Your Lakera Guard API key (required for security features)

### Security Manager Options

- `enable_tool_screening`: Screen tool descriptions during registration
- `enable_interaction_screening`: Screen server interactions
- `fail_on_violation`: Whether to raise exceptions on security violations

### CLI Security Options

- `--disable-security`: Disable all security screening
- `--lakera-api-key`: Override the environment variable API key

## Project Structure

```
simple_mcp_client/
├── src/
│   └── simple_mcp_client/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── client.py          # Single server MCP client
│       │   └── multi_client.py    # Multi-server MCP client
│       ├── security/              # 🔒 Security components
│       │   ├── __init__.py
│       │   ├── lakera_client.py   # Lakera Guard API client
│       │   └── security_manager.py # Security orchestration
│       ├── config/                # ⚙️ Configuration management
│       │   ├── __init__.py
│       │   └── server_config.py   # Server configuration
│       ├── utils/
│       │   ├── __init__.py
│       │   └── helpers.py
│       └── cli/
│           ├── __init__.py
│           └── main.py            # CLI with multi-server support
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_utils.py
│   └── test_security.py           # 🔒 Security tests
├── docs/
│   ├── conf.py
│   ├── index.rst
│   └── api.rst
├── examples/
│   ├── basic_usage.py
│   ├── security_demo.py           # 🔒 Security examples
│   └── multi_server_demo.py       # 🖥️ Multi-server examples
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Security Best Practices

1. **Always enable security screening** in production environments
2. **Use strict mode** (`fail_on_violation=True`) for sensitive applications
3. **Monitor security statistics** regularly
4. **Keep your Lakera API key secure** and never commit it to version control
5. **Regularly update** the client to get the latest security features
6. **Log security events** for audit purposes

## Multi-Server Best Practices

1. **Use descriptive server names** and tags for easy organization
2. **Set appropriate priorities** for servers based on reliability/performance
3. **Monitor server health** and tool availability
4. **Use configuration files** for persistent server management
5. **Implement fallback strategies** for critical tools
6. **Regularly refresh tool lists** when servers change

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the Model Context Protocol specification
- Built with modern Python best practices
- Uses Click for CLI interface
- **Security powered by [Lakera Guard](https://lakera.ai)**
- **Configuration pattern inspired by modern development tools** 