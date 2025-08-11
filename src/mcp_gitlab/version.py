"""Version utilities for mcp-gitlab."""

import sys
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def get_version() -> str:
    """Get version from pyproject.toml, fallback to hardcoded version."""
    try:
        if tomllib is None:
            return "0.1.0"  # Fallback for older Python without tomllib
            
        # Find pyproject.toml in package root
        current_file = Path(__file__)
        package_root = current_file.parent.parent.parent
        pyproject_path = package_root / "pyproject.toml"
        
        if not pyproject_path.exists():
            return "0.1.0"  # Fallback if file doesn't exist
            
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            
        return data.get("project", {}).get("version", "0.1.0")
    except Exception:
        # Fallback to hardcoded version if anything goes wrong
        return "0.1.0"


__version__ = get_version()