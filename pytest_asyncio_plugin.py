"""Very small asyncio plugin for pytest.

The real project depends on ``pytest-asyncio`` to run ``async def`` test
functions.  To keep the exercise self contained we provide a minimal
implementation that recognises ``@pytest.mark.asyncio`` and executes the test
coroutine using :func:`asyncio.run`.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any


def pytest_configure(config) -> None:  # pragma: no cover - plugin hook
    config.addinivalue_line("markers", "asyncio: mark test as an async coroutine")


def pytest_pyfunc_call(pyfuncitem):  # pragma: no cover - plugin hook
    if inspect.iscoroutinefunction(pyfuncitem.function):
        # Only pass fixtures that the test function actually expects to avoid
        # unexpected keyword arguments from autouse fixtures.
        kwargs = {
            name: pyfuncitem.funcargs[name]
            for name in pyfuncitem._fixtureinfo.argnames
        }
        coro = pyfuncitem.obj(**kwargs)
        asyncio.run(coro)
        return True
    return None

