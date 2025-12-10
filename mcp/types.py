"""Minimal subset of MCP type definitions used in the tests.

The original project relies on the `mcp` package (Model Context Protocol).  The
package is not available in the execution environment, so this module provides a
small collection of stand‑ins that mimic the interfaces used by the server and
the unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Tool:
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class TextContent:
    type: str
    text: str


@dataclass
class ImageContent:
    type: str
    data: Any | None = None


@dataclass
class EmbeddedResource:
    type: str
    data: Any | None = None


__all__ = [
    "Tool",
    "TextContent",
    "ImageContent",
    "EmbeddedResource",
]

