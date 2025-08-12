"""Minimal subset of exceptions used in the tests.

The real project depends on the `python-gitlab` package which provides a rich
set of exception classes.  The execution environment for the kata does not have
that dependency installed, therefore importing from :mod:`gitlab.exceptions`
would fail.  The tests only require a handful of exception types, so we provide
light‑weight stand‑ins that mimic the real hierarchy sufficiently for testing
purposes.
"""

class GitlabError(Exception):
    """Base class for all GitLab related errors."""


class GitlabHttpError(GitlabError):
    """HTTP level error returned by the GitLab API."""


class GitlabAuthenticationError(GitlabHttpError):
    """Raised when authentication with the GitLab API fails."""


class GitlabGetError(GitlabHttpError):
    """Raised for errors fetching resources from the API."""

    def __init__(self, *args, response_code: int | None = None, **kwargs):
        super().__init__(*args)
        # Tests access ``response_code`` to differentiate error types.
        self.response_code = response_code


class GitlabListError(GitlabHttpError):
    """Raised when listing resources fails."""


class GitlabCreateError(GitlabHttpError):
    """Raised when creating a resource fails."""


class GitlabUpdateError(GitlabHttpError):
    """Raised when updating a resource fails."""


class GitlabDeleteError(GitlabHttpError):
    """Raised when deleting a resource fails."""

