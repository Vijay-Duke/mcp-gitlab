"""Public package interface for mcp_gitlab.

The server component depends on the optional ``mcp`` package.  Importing it in
environments where the dependency is unavailable would raise an ImportError and
prevent access to the remaining utility modules.  To make the package more
robust for unit tests we try to import the server lazily and fall back to
lightweight placeholders when the import fails.
"""

from .gitlab_client import GitLabClient, GitLabConfig

__all__ = ["GitLabClient", "GitLabConfig"]

try:  # pragma: no cover - exercised implicitly during import
    from .server import server, main  # type: ignore
    __all__.extend(["server", "main"])
except Exception:  # pylint: disable=broad-except
    server = None  # type: ignore

    def main(*args, **kwargs):  # pragma: no cover - placeholder function
        raise ImportError("MCP server dependencies are not installed")

__version__ = "0.1.0"