#!/usr/bin/env python3
"""
Setup script for SearchAPI MCP Server Demo

This script helps you set up the environment needed to run the searchapi-mcp-server demo.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False


def check_command(command):
    """Check if a command is available."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def setup_environment():
    """Set up the environment for the demo."""
    print("🚀 Setting up SearchAPI MCP Server Demo Environment")
    print("=" * 60)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    node_available = check_command("node")
    npm_available = check_command("npm")
    git_available = check_command("git")
    
    print(f"  Node.js: {'✅ Available' if node_available else '❌ Not found'}")
    print(f"  npm: {'✅ Available' if npm_available else '❌ Not found'}")
    print(f"  git: {'✅ Available' if git_available else '❌ Not found'}")
    
    if not all([node_available, npm_available, git_available]):
        print("\n❌ Missing prerequisites. Please install:")
        if not node_available or not npm_available:
            print("  - Node.js and npm: https://nodejs.org/")
        if not git_available:
            print("  - Git: https://git-scm.com/")
        return False
    
    # Clone searchapi-mcp-server if not already present
    searchapi_dir = Path("../searchapi-mcp-server")
    if not searchapi_dir.exists():
        print("\n📥 Cloning searchapi-mcp-server...")
        if not run_command(
            "cd .. && git clone https://github.com/mrgoonie/searchapi-mcp-server.git",
            "Cloning searchapi-mcp-server repository"
        ):
            return False
    else:
        print("✅ searchapi-mcp-server already exists")
    
    # Install dependencies
    print("\n📦 Installing searchapi-mcp-server dependencies...")
    if not run_command(
        "cd ../searchapi-mcp-server && npm install",
        "Installing npm dependencies"
    ):
        return False
    
    # Check environment variables
    print("\n🔑 Checking environment variables...")
    searchapi_key = os.getenv("SEARCHAPI_API_KEY")
    lakera_key = os.getenv("LAKERA_GUARD_API_KEY")
    
    print(f"  SEARCHAPI_API_KEY: {'✅ Set' if searchapi_key else '❌ Not set'}")
    print(f"  LAKERA_GUARD_API_KEY: {'✅ Set' if lakera_key else '⚠️ Not set (optional)'}")
    
    if not searchapi_key:
        print("\n⚠️ SEARCHAPI_API_KEY not set. You'll need to:")
        print("  1. Sign up at https://searchapi.site/profile")
        print("  2. Get your API key")
        print("  3. Set the environment variable:")
        print("     export SEARCHAPI_API_KEY='your-api-key-here'")
    
    # Create .env file for searchapi-mcp-server
    env_file = Path("../searchapi-mcp-server/.env")
    if not env_file.exists():
        print("\n📝 Creating .env file for searchapi-mcp-server...")
        env_content = f"""# SearchAPI MCP Server Environment Variables
SEARCHAPI_API_KEY={searchapi_key or 'your-api-key-here'}
DEBUG=true
"""
        env_file.write_text(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Set your SEARCHAPI_API_KEY environment variable")
    print("2. Start the searchapi-mcp-server:")
    print("   cd ../searchapi-mcp-server")
    print("   npm run dev:server")
    print("3. In another terminal, run the demo:")
    print("   python examples/searchapi_integration_demo.py")
    
    return True


def start_server():
    """Start the searchapi-mcp-server."""
    print("\n🚀 Starting searchapi-mcp-server...")
    print("The server will be available at http://localhost:5173")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        subprocess.run(
            "cd ../searchapi-mcp-server && npm run dev:server",
            shell=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        start_server()
    else:
        setup_environment() 