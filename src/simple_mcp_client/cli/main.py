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
from ..security import SecurityManager, SecurityViolation
from ..utils.helpers import validate_url


@click.group()
@click.version_option()
def main():
    """Simple MCP Client - A lightweight client for the Model Context Protocol."""
    pass


@main.command()
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


@main.command()
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


@main.command()
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