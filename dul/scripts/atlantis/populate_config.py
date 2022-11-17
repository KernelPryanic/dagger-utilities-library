#!/usr/bin/env python3
"""
Script to be executed before commiting infra related code. It is used to update
Atlantis' configuration file

How to use (from root of monorepo):
```
# create virtual environment if not done yet
python3 -m venv .venv
source .venv/bin/activate
pip install -r pip-requirements.txt
pip install -r dev-requirements.txt
# To update the configuration file:
scripts/populate_atlantis_conf.py
# To check the configuration file:
scripts/populate_atlantis_conf.py --check
```

See the `main` and `__main__` function for more information on how this script handles arguments.
You can also get information from:
```
scripts/populate_atlantis_conf.py --help
```
"""

import argparse
from copy import deepcopy
from os import chdir, getcwd, path
from sys import exit
from typing import Dict, List

import hcl2
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as SQ

from common.git import git_ls_files, git_root_dir


def _add_types_path(acc: List[Dict], dir: str, extension: str, recursive: bool = True) -> List[str]:
    """Helper function to find files with a given `extension` in the directory `dir`, either
    recursively or not. It appends the results as dictionnaries in the `acc` variable.

    Args:
        acc: The list of dictionnaries to populate.
        dir: The directory of the terraform module to search.
        extension: The single extension to search.
        recursive: A boolean value indicating if the search should be recursive

    Returns:
        The list of files found.
    """
    search_path = dir + ("/**/*." if recursive else "/*.") + extension
    files_list = git_ls_files([search_path])
    if files_list:
        acc.append({"type": extension, "path": search_path})
    return files_list


def _resolve_module_paths(acc: List[Dict], dir: str) -> None:
    """
    Args:
        acc: The list of dictionnaries to populate.
        dir: The directory of the terraform module.

    Returns:
        Nothing.
    """
    # tf files
    tf_files = _add_types_path(acc, dir, "tf", False)
    if not tf_files:
        return
    # YAML/YML files
    _add_types_path(acc, dir, "yaml")
    _add_types_path(acc, dir, "yml")
    # TPL templates
    _add_types_path(acc, dir, "tpl")

    # modules
    def _get_module_source(module: dict) -> str:
        # module is a dictionnary with one key/value pair, where
        # - the key is the module name
        # - the values contain the module configuration

        # get module configuration as 'dict'
        kv = list(module.values())[0]
        # extract the source path
        source_path = kv.get("source")
        return source_path

    for file in tf_files:
        with open(file, "r") as fp:
            obj = hcl2.load(fp)
            modules = obj.get("module", [])
            res = [_get_module_source(module) for module in modules]
            for mod in res:
                acc.append({"type": "module", "path": mod})


def _resolve_atlantis_project_path(project_dir: str) -> List[str]:
    """
    Args:
        dir: The main directory of the terraform project.

    Returns:
        The list dependency of path of the terraform project.
    """
    # get original working directory
    CWD = getcwd()
    chdir(project_dir)
    index = 0
    acc = [{"type": "module", "path": "."}]
    while index < len(acc):
        if acc[index].get("type") == "module":
            dir = acc[index].get("path", "")
            acc.pop(index)
            _resolve_module_paths(acc, dir)
        else:
            index += 1
    # reset original working directory
    chdir(CWD)
    # get all values from path keys in acc
    res = [x.get("path", "") for x in acc]
    res = list(set(res))
    res.sort()
    return res


def _update_atlantis_project(atlantis_yaml: str, check: bool) -> int:
    """Function to get the updated the "when_modified" block of all "projects"
    in the atlantis configuration file.

    Args:
        atlantis_yaml: The path to atlantis' YAML configuration
        check: Wether to check if the updated configuration is the same as the
               current configuration file.

    Returns:
        None
    """

    def FSlist(paths: List[str]) -> CommentedSeq:
        # Helper function to create comment block-style lists
        cs = CommentedSeq([SQ(x) for x in paths])
        cs.fa.set_block_style()
        return cs

    yaml = YAML()
    setattr(yaml, "preserve_quotes", False)
    setattr(yaml, "explicit_start", True)
    yaml.indent(mapping=2, sequence=4, offset=2)
    with open(atlantis_yaml) as fp:
        data = yaml.load(fp)
    original_data = deepcopy(data)

    for project in data["projects"]:
        dir = project.get("dir")
        paths = _resolve_atlantis_project_path(dir)
        project["autoplan"]["when_modified"] = FSlist(paths)

    if not check:
        with open(atlantis_yaml, "w") as fp:
            yaml.dump(data, fp)
    else:
        if original_data != data:
            return 1
    return 0


def main(atlantis_yaml_file: str, check: bool) -> int:
    """The main function. It will launch the `_update_atlantis_project` function.

    Args:
        atlantis_yaml: The path to atlantis' YAML configuration.
                       If left empty, the path to atlantis' YAML configuration is determined
                       automatically. This will only work if the command is executed from within
                       the monorepo.
        check: Wether to check if the updated configuration is the same as the
               current configuration file.
    """
    # Get the repo's root directory
    github_root_dir = git_root_dir()
    # Set workding directory to repo's root.
    # This is becomes useful later as projects directories in the Atlantis' configuration
    # are relative to the repo's root dir
    chdir(github_root_dir)

    # Set atlantis_yaml_file to its default values (github_root_dir+"/atlantis.yaml")
    # if it is not given as input (None) or if it is empty
    if atlantis_yaml_file is None or not atlantis_yaml_file:
        atlantis_yaml_file = path.join(github_root_dir, "atlantis.yaml")

    return_code = _update_atlantis_project(atlantis_yaml_file, check)
    if check and return_code == 0:
        print("All done! ✨ 🍰 ✨")
        print("Atlantis configuration is correct.")
    elif check and return_code != 0:
        print("Oh no! 💥 💔 💥")
        print("Atlantis doesn't match the generated one.")

    return return_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="populate-atlantis")
    parser.add_argument(
        "--conf", help="Atlantis configuration file", default=None)
    parser.add_argument(
        "--check",
        default=False,
        help="Check if the populated atlantis configuration is similar to the existing file"
        + ".False if not set",
        action="store_true",
    )
    args = parser.parse_args()

    exit(main(args.conf, args.check))
