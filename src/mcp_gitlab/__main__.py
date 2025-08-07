#!/usr/bin/env python3
"""Main entry point for running mcp_gitlab as a module"""

import asyncio
import sys
from .server import main as async_main


def main():
    """Synchronous entry point for console script"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()