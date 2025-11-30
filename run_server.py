#!/usr/bin/env python3
"""
Simple script to run Competitive Intelligence & Daily Planning MCP server.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from server import mcp

def main():
    """Run FastMCP server."""
    # Check for required environment variables
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        return 1
    
    # Run FastMCP server
    print("Starting Competitive Intelligence & Daily Planning MCP server...")
    mcp.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
