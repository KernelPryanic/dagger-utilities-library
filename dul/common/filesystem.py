import fnmatch
import os


def find_files(path, name: str) -> list[str]:
    matches: list[str] = []
    for root, _, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, name):
            matches.append(os.path.join(root, filename))

    return matches
