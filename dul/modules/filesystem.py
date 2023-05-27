"""Filesystem utilities."""

import fnmatch
import os

from typing import Generator


def find_files(path, name: str) -> Generator[str, None, None]:
    """Find files matching a pattern in a directory tree.

    Args:
        path (str): Path to search
        name (str): Filename pattern to match

    Yields:
        Generator[str, None, None]: Generator of matching filenames.
    """

    for root, _, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, name):
            yield os.path.join(root, filename)
