"""Git helper functions in python."""

from __future__ import annotations

import os
import re
from typing import Generator

from git import Blob, Repo


class GitRepo:
    """Extended Git repository object.

    Args:
        path (str, optional): The path to the git repo. Defaults to ".".
        repo (Repo, optional): The git repo object. Defaults to None.
        blobs (Generator[Blob, None, None], optional): The generator of blobs in the git repo. Defaults to None.

    Returns:
        GitRepo: The extended git repo object.
    """

    def __init__(
        self,
        path: str = ".",
        repo: Repo = None,
        blobs: Generator[Blob, None, None] = None,
        *args,
        **kwargs,
    ):
        if repo is not None:
            self.repo = repo
        else:
            self.repo = Repo(path, search_parent_directories=True, *args, **kwargs)
        self.blobs: Generator[Blob, None, None]
        if blobs is not None:
            self.blobs = blobs

    def get_root(self) -> str:
        """Get the root directory of the git repo.

        Returns:
            str: The root directory of the git repo.
        """

        return self.repo.working_tree_dir

    def get_blobs(self) -> GitRepo:
        """Get the list of blobs in the git repo.

        Returns:
            GitRepo: A new instance of GitRepo with the generator of all blobs in the git repo.
        """

        def get_blobs():
            if not self.repo.bare:
                commit = self.repo.head.commit
                for blob in commit.tree.traverse():
                    if blob.type == "blob":
                        yield blob

        return GitRepo(repo=self.repo, blobs=get_blobs())

    def get_lfs_blobs(self) -> GitRepo:
        """Get the list of LFS blobs in the git repo.

        Returns:
            GitRepo: A new instance of GitRepo with the generator of LFS blobs in the git repo.
        """

        def get_lfs_blobs():
            for blob in self.blobs:
                if self.is_lfs_blob(blob):
                    yield blob

        return GitRepo(repo=self.repo, blobs=get_lfs_blobs())

    def find_blobs(self, pattern: str) -> GitRepo:
        """Get the list of blobs matching the pattern.

        Args:
            pattern (str): The pattern to match.

        Returns:
            GitRepo: A new instance of GitRepo with the generator of blobs matching the pattern.
        """

        def find_blobs():
            for blob in self.blobs:
                if re.search(pattern, os.path.basename(blob.path)):
                    yield blob

        return GitRepo(repo=self.repo, blobs=find_blobs())

    @classmethod
    def is_lfs_blob(cls, blob: Blob) -> bool:
        """Check if the blob belongs to LFS.

        Args:
            blob (Blob): The blob to check.

        Returns:
            bool: True if the blob belongs to LFS.
        """

        content = blob.data_stream.read(42).decode("utf-8")
        return content.startswith("version https://git-lfs.github.com/spec/v1")
