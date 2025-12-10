"""Lightweight stubs of the MCP server classes used in the tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Awaitable, Dict


class Server:
    """Very small stand‑in for the real MCP ``Server`` class.

    The decorators simply return the wrapped function unchanged which is
    sufficient for the unit tests that call the handlers directly.
    """

    def __init__(self, name: str):
        self.name = name

    def list_tools(self) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
        def decorator(func: Callable[..., Awaitable[Any]]):
            return func
        return decorator

    def call_tool(self) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
        def decorator(func: Callable[..., Awaitable[Any]]):
            return func
        return decorator

    # Methods used in ``main`` but irrelevant for the tests ---------------------------------
    def get_capabilities(self, **_: Any) -> Dict[str, Any]:  # pragma: no cover - simple stub
        return {}

    async def run(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - simple stub
        return None


@dataclass
class NotificationOptions:  # pragma: no cover - trivial container
    pass


__all__ = ["Server", "NotificationOptions"]

