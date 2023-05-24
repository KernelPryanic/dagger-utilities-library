"""Git helper functions in python."""

from __future__ import annotations

import os
import re
from typing import Generator

from git import Blob, Repo


class GitRepo(Repo):
    """Extended Git repository object."""

    def __init__(self, path: str = ".", *args, **kwargs):
        Repo.__init__(self, path, search_parent_directories=True, *args, **kwargs)
        self.blobs: Generator[Blob, None, None]

    def get_root(self) -> str:
        """Get the root directory of the git repo.

        Args:
            path (str): The path to the file or directory.

        Returns:
            str: The root directory of the git repo.
        """

        return self.working_tree_dir

    def get_blobs(self) -> GitRepo:
        """Get the list of blobs in the git repo.

        Returns:
            Generator[Blob, None, None]: A generator of blobs in the git repo.
        """

        def get_blobs():
            if not self.bare:
                commit = self.head.commit
                for blob in commit.tree.traverse():
                    if blob.type == "blob":
                        yield blob

        self.blobs = get_blobs()

        return self

    def get_lfs_blobs(self) -> GitRepo:
        """Get the list of LFS blobs in the git repo.

        Returns:
            Generator[Blob, None, None]: A generator of LFS blobs in the git repo.
        """

        def get_lfs_blobs():
            for blob in self.blobs:
                if self.is_lfs_blob(blob):
                    yield blob

        self.blobs = get_lfs_blobs()

        return self

    def find_blobs(self, pattern: str) -> GitRepo:
        """Get the list of blobs matching the pattern.

        Args:
            pattern (str): The pattern to match.

        Returns:
            Generator[Blob, None, None]: A generator of blobs matching the pattern.
        """

        def find_blobs():
            for blob in self.blobs:
                if re.search(pattern, os.path.basename(blob.path)):
                    yield blob

        # self.blobs = find_blobs()
        c = GitRepo(self.working_tree_dir)
        c.blobs = find_blobs()

        return c

    @classmethod
    def is_lfs_blob(cls, blob: Blob) -> bool:
        """Check if the blob belongs to lfs.

        Args:
            blob (Blob): The blob to check.

        Returns:
            bool: True if the blob belongs to lfs.
        """

        content = blob.data_stream.read(42).decode("utf-8")
        return content.startswith("version https://git-lfs.github.com/spec/v1")
