"""Compatibility wrapper package for the test suite.

This project uses a ``src`` layout where the real package lives in
``src/mcp_gitlab``.  The unit tests import ``mcp_gitlab`` directly from the
repository root without installing the package which normally leaves the
modules undiscoverable.  To make imports succeed we expose a lightweight
package at the repository root which simply adds the ``src`` directory to the
package search path.

Having this file allows ``import mcp_gitlab.git_detector`` (and other modules)
to resolve correctly during the tests without requiring an editable install or
modifying ``PYTHONPATH``.
"""

from __future__ import annotations

from pathlib import Path
import pkgutil

# Extend the package search path to include the real source directory.  This
# makes Python look inside ``src/mcp_gitlab`` when resolving submodules.
__path__ = pkgutil.extend_path(__path__, __name__)  # type: ignore[name-defined]

_src_path = Path(__file__).resolve().parent.parent / "src" / "mcp_gitlab"
if _src_path.is_dir() and str(_src_path) not in __path__:
    __path__.append(str(_src_path))

# Re-export the package version if it exists.  The actual ``__init__`` inside
# ``src/mcp_gitlab`` is empty so this is primarily for completeness.
__all__: list[str] = []

