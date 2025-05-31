#!/usr/bin/env python3
"""
Setup script for Email Marketing MCP Server
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment configuration"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your API credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.example file not found")
        return False

def test_installation():
    """Test the installation"""
    print("Testing installation...")
    try:
        # Import the server module to check for syntax errors
        import importlib.util
        spec = importlib.util.spec_from_file_location("server", "server.py")
        server_module = importlib.util.module_from_spec(spec)
        
        # Mock the MCP server to avoid running it
        class MockMCP:
            def __init__(self, name): pass
            def tool(self): return lambda f: f
            def run(self): pass
        
        # Replace the FastMCP import
        sys.modules['mcp.server.fastmcp'] = type('MockModule', (), {'FastMCP': MockMCP})
        
        spec.loader.exec_module(server_module)
        print("✅ Server module loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load server module: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your email provider credentials:")
    print("   - For SendGrid: Get API key from https://sendgrid.com")
    print("   - For Mailchimp: Get API key from your Mailchimp account")
    print("\n2. Test your connection:")
    print("   python test_connection.py sendgrid YOUR_API_KEY")
    print("   # or")
    print("   python test_connection.py mailchimp YOUR_API_KEY")
    print("\n3. Test the MCP tools:")
    print("   python test_tools.py")
    print("\n4. Start the MCP server:")
    print("   python server.py --email-key YOUR_API_KEY --email-provider sendgrid")
    print("\n5. Configure in Claude Desktop (optional):")
    print("   Add server configuration to claude_desktop_config.json")
    print("\nFor detailed documentation, see README.md")

def main():
    """Main setup function"""
    print("Email Marketing MCP Server Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Setup environment
    if success and not setup_environment():
        success = False
    
    # Test installation
    if success and not test_installation():
        success = False
    
    if success:
        show_next_steps()
    else:
        print("\n💥 Setup failed! Please check the errors above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()