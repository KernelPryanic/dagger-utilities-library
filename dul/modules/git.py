"""Git helper functions in python."""

import os
from typing import Generator

from git import Blob, Repo


class GitRepo(Repo):
    """Extended Git repository object."""

    def __init__(self, path: str = ".", *args, **kwargs):
        Repo.__init__(self, path, search_parent_directories=True, *args, **kwargs)

    def get_root(self) -> str:
        """Get the root directory of the git repo.

        Args:
            path (str): The path to the file or directory.

        Returns:
            str: The root directory of the git repo.
        """

        return self.working_tree_dir

    @classmethod
    def is_lsf_file(cls, blob: Blob) -> bool:
        """Check if the blob is a LFS file.

        Args:
            blob (Blob): The blob to check.

        Returns:
            bool: True if the blob is a LFS file.
        """

        content = blob.data_stream.read(42).decode("utf-8")
        return content.startswith("version https://git-lfs.github.com/spec/v1")

    def get_lfs_files(self) -> Generator[str, None, None]:
        """Get the list of LFS files in the git repo.

        Returns:
            Generator[str, None, None]: A generator of LFS files in the git repo.
        """

        if not self.bare:
            commit = self.head.commit
            for blob in commit.tree.traverse():
                if blob.type == "blob" and self.is_lsf_file(blob):
                    yield blob.path

    def find_files(self, regex: str) -> Generator[str, None, None]:
        """Get the list of files matching the regex.

        Args:
            regex (str): The regex to match.

        Returns:
            Generator[str, None, None]: A generator of files matching the regex.
        """

        if not self.bare:
            commit = self.head.commit
            for blob in commit.tree.traverse():
                if blob.type == "blob" and os.path.basename(blob.path).match(regex):
                    yield blob.path
