"""Filesystem utilities."""

import fnmatch
import os


def find_files(path, name: str) -> list[str]:
    """Find files matching a pattern in a directory tree.

    Args:
        path (str): Path to search
        name (str): Filename pattern to match

    Returns:
        list[str]: List of matching filenames
    """

    matches: list[str] = []
    for root, _, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, name):
            matches.append(os.path.join(root, filename))

    return matches
