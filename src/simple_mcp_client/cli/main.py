"""
Command-line interface main module.

This module provides the main CLI entry point for the Simple MCP Client.
"""

import json
import os
import sys
from typing import Optional

import click

from ..core.client import MCPClient
from ..core.multi_client import MultiMCPClient
from ..config import add_server_config, list_server_configs, remove_server_config, load_config
from ..security import SecurityManager, SecurityViolation
from ..utils.helpers import validate_url


@click.group()
@click.version_option()
def main():
    """Simple MCP Client - A lightweight client for the Model Context Protocol."""
    pass


# Single server commands
@main.group()
def server():
    """Single server operations."""
    pass


@server.command()
@click.option('--server-url', '-u', required=True, help='MCP server URL')
@click.option('--timeout', '-t', default=30, help='Request timeout in seconds')
@click.option('--disable-security', is_flag=True, help='Disable security screening')
@click.option('--lakera-api-key', help='Lakera API key (overrides LAKERA_GUARD_API_KEY env var)')
def connect(server_url: str, timeout: int, disable_security: bool, lakera_api_key: Optional[str]):
    """Test connection to an MCP server."""
    if not validate_url(server_url):
        click.echo(f"Error: Invalid URL format: {server_url}", err=True)
        sys.exit(1)
    
    try:
        # Set up security if enabled
        security_manager = None
        if not disable_security:
            if lakera_api_key:
                os.environ['LAKERA_GUARD_API_KEY'] = lakera_api_key
            try:
                security_manager = SecurityManager()
                click.echo("🔒 Security screening enabled")
            except ValueError as e:
                click.echo(f"⚠️  Security disabled: {e}", err=True)
        else:
            click.echo("⚠️  Security screening disabled")
        
        with MCPClient(server_url, timeout, security_manager, not disable_security) as client:
            if client.connect():
                click.echo(f"✅ Successfully connected to {server_url}")
                
                # Show security stats if available
                stats = client.get_security_stats()
                if stats:
                    click.echo(f"📊 Security stats: {stats['interactions_screened']} interactions screened")
            else:
                click.echo(f"❌ Failed to connect to {server_url}", err=True)
                sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@server.command()
@click.option('--server-url', '-u', required=True, help='MCP server URL')
@click.option('--timeout', '-t', default=30, help='Request timeout in seconds')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.option('--disable-security', is_flag=True, help='Disable security screening')
@click.option('--lakera-api-key', help='Lakera API key (overrides LAKERA_GUARD_API_KEY env var)')
def list_tools(server_url: str, timeout: int, output: Optional[str], disable_security: bool, lakera_api_key: Optional[str]):
    """List available tools from an MCP server."""
    if not validate_url(server_url):
        click.echo(f"Error: Invalid URL format: {server_url}", err=True)
        sys.exit(1)
    
    try:
        # Set up security if enabled
        security_manager = None
        if not disable_security:
            if lakera_api_key:
                os.environ['LAKERA_GUARD_API_KEY'] = lakera_api_key
            try:
                security_manager = SecurityManager()
                click.echo("🔒 Security screening enabled")
            except ValueError as e:
                click.echo(f"⚠️  Security disabled: {e}", err=True)
        else:
            click.echo("⚠️  Security screening disabled")
        
        with MCPClient(server_url, timeout, security_manager, not disable_security) as client:
            response = client.list_tools()
            
            if response.error:
                click.echo(f"Error: {response.error}", err=True)
                sys.exit(1)
            
            result = response.result or {}
            tools = result.get('tools', [])
            
            if output:
                with open(output, 'w') as f:
                    json.dump(tools, f, indent=2)
                click.echo(f"Tools list saved to {output}")
            else:
                if tools:
                    click.echo(f"Found {len(tools)} tool(s):")
                    for tool in tools:
                        name = tool.get('name', 'Unknown')
                        description = tool.get('description', 'No description')
                        click.echo(f"  - {name}: {description}")
                else:
                    click.echo("No tools available")
            
            # Show security stats
            stats = client.get_security_stats()
            if stats and stats['tools_screened'] > 0:
                click.echo(f"\n🔒 Security: {stats['tools_screened']} tools screened, "
                          f"{stats['violations_detected']} violations detected")
                    
    except SecurityViolation as e:
        click.echo(f"🚨 Security violation: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@server.command()
@click.option('--server-url', '-u', required=True, help='MCP server URL')
@click.option('--tool-name', '-n', required=True, help='Name of the tool to call')
@click.option('--arguments', '-a', help='Tool arguments as JSON string')
@click.option('--timeout', '-t', default=30, help='Request timeout in seconds')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.option('--disable-security', is_flag=True, help='Disable security screening')
@click.option('--lakera-api-key', help='Lakera API key (overrides LAKERA_GUARD_API_KEY env var)')
def call_tool(server_url: str, tool_name: str, arguments: Optional[str], timeout: int, output: Optional[str], disable_security: bool, lakera_api_key: Optional[str]):
    """Call a specific tool on an MCP server."""
    if not validate_url(server_url):
        click.echo(f"Error: Invalid URL format: {server_url}", err=True)
        sys.exit(1)
    
    # Parse arguments
    tool_args = {}
    if arguments:
        try:
            tool_args = json.loads(arguments)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON format for arguments", err=True)
            sys.exit(1)
    
    try:
        # Set up security if enabled
        security_manager = None
        if not disable_security:
            if lakera_api_key:
                os.environ['LAKERA_GUARD_API_KEY'] = lakera_api_key
            try:
                security_manager = SecurityManager()
                click.echo("🔒 Security screening enabled")
            except ValueError as e:
                click.echo(f"⚠️  Security disabled: {e}", err=True)
        else:
            click.echo("⚠️  Security screening disabled")
        
        with MCPClient(server_url, timeout, security_manager, not disable_security) as client:
            response = client.call_tool(tool_name, tool_args)
            
            if response.error:
                click.echo(f"Error: {response.error}", err=True)
                sys.exit(1)
            
            result = response.result or {}
            
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2)
                click.echo(f"Tool result saved to {output}")
            else:
                click.echo(json.dumps(result, indent=2))
            
            # Show security stats
            stats = client.get_security_stats()
            if stats and stats['interactions_screened'] > 0:
                click.echo(f"\n🔒 Security: {stats['interactions_screened']} interactions screened, "
                          f"{stats['violations_detected']} violations detected")
                
    except SecurityViolation as e:
        click.echo(f"🚨 Security violation: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Multi-server commands
@main.group()
def multi():
    """Multi-server operations."""
    pass


@multi.command()
@click.option('--name', '-n', required=True, help='Server name')
@click.option('--url', '-u', required=True, help='Server URL')
@click.option('--description', '-d', help='Server description')
@click.option('--timeout', '-t', default=30, help='Request timeout')
@click.option('--priority', '-p', default=0, help='Server priority (higher = preferred)')
@click.option('--tags', help='Comma-separated tags')
@click.option('--disabled', is_flag=True, help='Add server as disabled')
def add_server(name: str, url: str, description: Optional[str], timeout: int, priority: int, tags: Optional[str], disabled: bool):
    """Add a server to the configuration."""
    if not validate_url(url):
        click.echo(f"Error: Invalid URL format: {url}", err=True)
        sys.exit(1)
    
    tag_list = tags.split(',') if tags else []
    tag_list = [tag.strip() for tag in tag_list if tag.strip()]
    
    success = add_server_config(
        name=name,
        url=url,
        description=description,
        enabled=not disabled,
        timeout=timeout,
        priority=priority,
        tags=tag_list
    )
    
    if not success:
        sys.exit(1)


@multi.command()
@click.option('--name', '-n', required=True, help='Server name to remove')
def remove_server(name: str):
    """Remove a server from the configuration."""
    success = remove_server_config(name)
    if not success:
        sys.exit(1)


@multi.command()
def list_servers():
    """List all configured servers."""
    servers = list_server_configs()
    
    if not servers:
        click.echo("No servers configured")
        return
    
    click.echo(f"Configured servers ({len(servers)}):")
    for server in servers:
        status = "✅ Enabled" if server.enabled else "❌ Disabled"
        click.echo(f"  - {server.name} ({server.url}) [{status}]")
        if server.description:
            click.echo(f"    Description: {server.description}")
        if server.tags:
            click.echo(f"    Tags: {', '.join(server.tags)}")
        click.echo(f"    Priority: {server.priority}, Timeout: {server.timeout}s")


@multi.command()
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.option('--disable-security', is_flag=True, help='Disable security screening')
@click.option('--lakera-api-key', help='Lakera API key (overrides LAKERA_GUARD_API_KEY env var)')
def list_all_tools(output: Optional[str], disable_security: bool, lakera_api_key: Optional[str]):
    """List all tools from all configured servers."""
    config = load_config()
    enabled_servers = [s for s in config.servers if s.enabled]
    
    if not enabled_servers:
        click.echo("No enabled servers configured")
        return
    
    # Set up security if enabled
    security_manager = None
    if not disable_security:
        if lakera_api_key:
            os.environ['LAKERA_GUARD_API_KEY'] = lakera_api_key
        try:
            security_manager = SecurityManager()
            click.echo("🔒 Security screening enabled")
        except ValueError as e:
            click.echo(f"⚠️  Security disabled: {e}", err=True)
    else:
        click.echo("⚠️  Security screening disabled")
    
    try:
        with MultiMCPClient(security_manager=security_manager, enable_security=not disable_security) as client:
            # Add all enabled servers
            for server_config in enabled_servers:
                if client.add_server(server_config.url):
                    click.echo(f"✅ Connected to {server_config.name} ({server_config.url})")
                else:
                    click.echo(f"❌ Failed to connect to {server_config.name} ({server_config.url})")
            
            # Get all tools
            tools = client.list_tools()
            
            if output:
                # Save tool information
                tool_data = []
                for tool in tools:
                    tool_data.append({
                        "name": tool.name,
                        "description": tool.description,
                        "server": tool.server_url,
                        "parameters": tool.parameters
                    })
                
                with open(output, 'w') as f:
                    json.dump(tool_data, f, indent=2)
                click.echo(f"Tools list saved to {output}")
            else:
                if tools:
                    click.echo(f"\nFound {len(tools)} tool(s) across {len(client.servers)} server(s):")
                    for tool in tools:
                        click.echo(f"  - {tool.name}: {tool.description}")
                        click.echo(f"    Server: {tool.server_url}")
                else:
                    click.echo("No tools available")
            
            # Show statistics
            stats = client.get_stats()
            click.echo(f"\n📊 Statistics: {stats['total_servers']} servers, {stats['total_tools']} tools")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@multi.command()
@click.option('--tool-name', '-n', required=True, help='Name of the tool to call')
@click.option('--arguments', '-a', help='Tool arguments as JSON string')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.option('--disable-security', is_flag=True, help='Disable security screening')
@click.option('--lakera-api-key', help='Lakera API key (overrides LAKERA_GUARD_API_KEY env var)')
def call_tool_multi(tool_name: str, arguments: Optional[str], output: Optional[str], disable_security: bool, lakera_api_key: Optional[str]):
    """Call a tool by name across all configured servers."""
    config = load_config()
    enabled_servers = [s for s in config.servers if s.enabled]
    
    if not enabled_servers:
        click.echo("No enabled servers configured")
        sys.exit(1)
    
    # Parse arguments
    tool_args = {}
    if arguments:
        try:
            tool_args = json.loads(arguments)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON format for arguments", err=True)
            sys.exit(1)
    
    # Set up security if enabled
    security_manager = None
    if not disable_security:
        if lakera_api_key:
            os.environ['LAKERA_GUARD_API_KEY'] = lakera_api_key
        try:
            security_manager = SecurityManager()
            click.echo("🔒 Security screening enabled")
        except ValueError as e:
            click.echo(f"⚠️  Security disabled: {e}", err=True)
    else:
        click.echo("⚠️  Security screening disabled")
    
    try:
        with MultiMCPClient(security_manager=security_manager, enable_security=not disable_security) as client:
            # Add all enabled servers
            for server_config in enabled_servers:
                client.add_server(server_config.url)
            
            # Find the tool
            tool = client.find_tool(tool_name)
            if not tool:
                click.echo(f"Error: Tool '{tool_name}' not found on any server")
                sys.exit(1)
            
            click.echo(f"Found tool '{tool_name}' on server {tool.server_url}")
            
            # Call the tool
            response = client.call_tool(tool_name, tool_args)
            
            if response.error:
                click.echo(f"Error: {response.error}", err=True)
                sys.exit(1)
            
            result = response.result or {}
            
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2)
                click.echo(f"Tool result saved to {output}")
            else:
                click.echo(json.dumps(result, indent=2))
            
            # Show statistics
            stats = client.get_stats()
            click.echo(f"\n📊 Statistics: {stats['requests_routed']} requests routed")
            
    except SecurityViolation as e:
        click.echo(f"🚨 Security violation: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Security commands
@main.command()
@click.option('--content', '-c', required=True, help='Content to screen')
@click.option('--lakera-api-key', help='Lakera API key (overrides LAKERA_GUARD_API_KEY env var)')
@click.option('--detailed', is_flag=True, help='Show detailed threat categories')
def screen(content: str, lakera_api_key: Optional[str], detailed: bool):
    """Screen content using Lakera Guard."""
    try:
        if lakera_api_key:
            os.environ['LAKERA_GUARD_API_KEY'] = lakera_api_key
        
        from ..security import LakeraClient
        
        with LakeraClient() as client:
            response = client.screen_content(content, include_dev_info=detailed)
            
            if response.flagged:
                click.echo("🚨 Content flagged as potentially unsafe")
                if detailed:
                    click.echo(f"Categories: {response.categories}")
                    click.echo(f"Scores: {response.category_scores}")
                    if response.dev_info:
                        click.echo(f"Guard version: {response.dev_info.get('version', 'Unknown')}")
            else:
                click.echo("✅ Content appears safe")
                if detailed and response.dev_info:
                    click.echo(f"Guard version: {response.dev_info.get('version', 'Unknown')}")
                    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 