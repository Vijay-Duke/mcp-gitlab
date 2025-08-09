"""Root level pytest configuration.

This file loads the lightweight asyncio plugin implemented in
``pytest_asyncio_plugin`` so that tests marked with ``@pytest.mark.asyncio`` are
executed correctly without requiring the external ``pytest-asyncio``
dependency.
"""

pytest_plugins = ["pytest_asyncio_plugin"]

