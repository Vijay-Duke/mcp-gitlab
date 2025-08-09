"""Stub models used by the tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InitializationOptions:  # pragma: no cover - simple container
    server_name: str | None = None
    server_version: str | None = None
    capabilities: dict | None = None


__all__ = ["InitializationOptions"]

