"""
Git helper functions in python
"""

import os
import subprocess
from typing import List


def command_output(cmd: List[str]) -> str:
    """Function execute commands and returns the standard output as a list of string.

    Args:
        cmd: The command to execute.

    Returns:
        The command output as a list of string.
    """
    if not cmd or cmd is None:
        print(":error:")
        print("Command is empty.")
        exit(1)
    try:
        sub = subprocess.run(
            cmd, universal_newlines=True, capture_output=True, text=True, check=True
        )
    except Exception as exc:
        print(":error:")
        print(exc)
        exit(1)
    return sub.stdout


def git_root_dir() -> str:
    """Function to get the root directory of a git repo

    Returns:
        git's root directory path
    """
    cmd = ["git", "rev-parse", "--show-toplevel"]
    sub = command_output(cmd)
    res = sub.rstrip()
    return res


def git_ls_files(files: List[str] = []) -> List[str]:
    """Function to get the list of files in of a git repo

    Args:
        files: Files to show. If no files are given all files which match the other specified
               criteria are shown. See the `<file>` argument in `git ls-files`.
    Returns:
        Output of `git ls-files` with the given arguments
    """
    cmd = ["git", "ls-files"]
    cmd += files
    sub = command_output(cmd)
    res = sub.rstrip().split("\n")
    res = list(filter(len, res))
    return res


def git_lfs_files() -> List[str]:
    """Function to get the list of LFS files in of a git repo

    Returns:
        Output of `git lfs ls -n` with the given arguments
    """
    cmd = ["git", "lfs", "ls-files", "-n"]
    sub = command_output(cmd)
    res = sub.rstrip().split("\n")
    res = list(filter(len, res))
    return res


def git_find_files(dir: str = ".", args: List[str] = []) -> List[str]:
    """Function to get the list of intersecting files matching the `find` command and
    `git lf-files`.

    Args:
        dir: The directory to search
        args: Extra arguments for the `find` command. See `man find`.

    Returns:
        A list of files.
    """
    cmd = ["find", dir, "-type", "f"]
    cmd += args
    # get files with `find`
    sub = command_output(cmd)
    files_find = sub.rstrip().split("\n")
    files_find = list(filter(len, files_find))
    files_find = list(map(os.path.normpath, files_find))
    # get git files
    files_git = git_ls_files([dir])
    # intersection of `files_find` and `files_git`
    res = list(set(files_find) & set(files_git))
    return res
