"""Stub implementation of ``mcp.server.stdio`` used only for tests."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Tuple


@asynccontextmanager
async def stdio_server() -> AsyncIterator[Tuple[Any, Any]]:  # pragma: no cover - trivial stub
    yield None, None


__all__ = ["stdio_server"]

