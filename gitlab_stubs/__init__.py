"""A very small stub of the :mod:`gitlab` package used for tests.

The real project depends on the third‑party `python-gitlab` library.  For the
kata the dependency is intentionally absent, so this stub provides just enough
functionality for the code under test to run.  Only the pieces required by the
tests are implemented: a :class:`Gitlab` client class and an ``exceptions``
submodule.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import exceptions  # re-export for convenience


@dataclass
class Gitlab:
    """Very small stand‑in for :class:`python_gitlab.Gitlab`.

    The class simply stores the URL and authentication arguments.  The real
    client exposes many methods; however in the tests the instance is always
    replaced with a :class:`unittest.mock.Mock`, so the implementation here only
    needs an ``auth`` method that does nothing.
    """

    url: str
    private_token: str | None = None
    oauth_token: str | None = None

    def auth(self) -> None:  # pragma: no cover - trivial stub
        """Pretend to authenticate with the server."""


__all__ = ["Gitlab", "exceptions"]

