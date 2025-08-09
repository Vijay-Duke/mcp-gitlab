"""Lightweight stand-ins for optional third-party dependencies used in tests.

This module registers very small placeholder implementations for libraries
that the project interacts with but are not required for running the test
suite.  The stubs are intentionally minimal and only provide the interfaces
that the unit tests touch.  They are imported for their side effects from
``conftest``.
"""

import sys
import types


# ---------------------------------------------------------------------------
# gitlab stubs
# ---------------------------------------------------------------------------

if "gitlab" not in sys.modules:
    gitlab_module = types.ModuleType("gitlab")
    exceptions_module = types.ModuleType("gitlab.exceptions")
    v4_module = types.ModuleType("gitlab.v4")
    objects_module = types.ModuleType("gitlab.v4.objects")

    class Gitlab:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    class Project:  # pragma: no cover - simple stub
        pass

    class Issue:  # pragma: no cover - simple stub
        pass

    class MergeRequest:  # pragma: no cover - simple stub
        pass

    gitlab_module.Gitlab = Gitlab
    gitlab_module.exceptions = exceptions_module
    gitlab_module.v4 = v4_module
    v4_module.objects = objects_module
    objects_module.Project = Project
    objects_module.Issue = Issue
    objects_module.MergeRequest = MergeRequest

    class GitlabError(Exception):
        pass

    class GitlabGetError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabAuthenticationError(GitlabError):
        pass

    class GitlabHttpError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabListError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabCreateError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabUpdateError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    class GitlabDeleteError(GitlabError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.response_code = kwargs.get("response_code")

    exceptions_module.GitlabError = GitlabError
    exceptions_module.GitlabGetError = GitlabGetError
    exceptions_module.GitlabAuthenticationError = GitlabAuthenticationError
    exceptions_module.GitlabHttpError = GitlabHttpError
    exceptions_module.GitlabListError = GitlabListError
    exceptions_module.GitlabCreateError = GitlabCreateError
    exceptions_module.GitlabUpdateError = GitlabUpdateError
    exceptions_module.GitlabDeleteError = GitlabDeleteError

    sys.modules["gitlab"] = gitlab_module
    sys.modules["gitlab.exceptions"] = exceptions_module
    sys.modules["gitlab.v4"] = v4_module
    sys.modules["gitlab.v4.objects"] = objects_module


# ---------------------------------------------------------------------------
# mcp stubs
# ---------------------------------------------------------------------------

if "mcp" not in sys.modules:
    mcp_module = types.ModuleType("mcp")
    server_module = types.ModuleType("mcp.server")
    models_module = types.ModuleType("mcp.server.models")
    stdio_module = types.ModuleType("mcp.server.stdio")
    types_module = types.ModuleType("mcp.types")

    class Server:  # pragma: no cover - simple stub
        """Very small stand-in for mcp.server.Server used in tests."""

        def __init__(self, *args, **kwargs):
            pass

        def list_tools(self):  # pragma: no cover - simple stub
            def decorator(func):
                return func

            return decorator

        def call_tool(self):  # pragma: no cover - simple stub
            def decorator(func):
                return func

            return decorator

        def get_capabilities(self, *args, **kwargs):  # pragma: no cover - stub
            return {}

        async def run(self, *args, **kwargs):  # pragma: no cover - stub
            return None

    class NotificationOptions:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    class InitializationOptions:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    def stdio_server(*args, **kwargs):  # pragma: no cover - simple stub
        pass

    class Tool:  # pragma: no cover - simple stub
        def __init__(self, name, description="", inputSchema=None):
            self.name = name
            self.description = description
            self.inputSchema = inputSchema

    class TextContent:  # pragma: no cover - simple stub
        def __init__(self, type="text", text=""):
            self.type = type
            self.text = text

    class ImageContent:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    class EmbeddedResource:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

    server_module.Server = Server
    server_module.NotificationOptions = NotificationOptions
    stdio_module.stdio_server = stdio_server
    models_module.InitializationOptions = InitializationOptions

    types_module.Tool = Tool
    types_module.TextContent = TextContent
    types_module.ImageContent = ImageContent
    types_module.EmbeddedResource = EmbeddedResource

    mcp_module.server = server_module
    mcp_module.types = types_module

    sys.modules["mcp"] = mcp_module
    sys.modules["mcp.server"] = server_module
    sys.modules["mcp.server.models"] = models_module
    sys.modules["mcp.server.stdio"] = stdio_module
    sys.modules["mcp.types"] = types_module


# ---------------------------------------------------------------------------
# pydantic stubs
# ---------------------------------------------------------------------------

try:  # pragma: no cover - tiny stand-ins only used if pydantic is absent
    import pydantic  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
    pydantic_module = types.ModuleType("pydantic")

    class BaseModel:  # pragma: no cover - simple stub
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(default=None, **kwargs):  # pragma: no cover - simple stub
        return default

    class AnyUrl(str):  # pragma: no cover - simple stub
        pass

    pydantic_module.BaseModel = BaseModel
    pydantic_module.Field = Field
    pydantic_module.AnyUrl = AnyUrl
    sys.modules["pydantic"] = pydantic_module


# ---------------------------------------------------------------------------
# python-dotenv stubs
# ---------------------------------------------------------------------------

if "dotenv" not in sys.modules:
    dotenv_module = types.ModuleType("dotenv")

    def load_dotenv(*args, **kwargs):  # pragma: no cover - simple stub
        return None

    dotenv_module.load_dotenv = load_dotenv
    sys.modules["dotenv"] = dotenv_module

