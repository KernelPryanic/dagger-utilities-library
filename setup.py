import importlib
import os
import sys
from os.path import join
from typing import List

from setuptools import find_namespace_packages, setup


def parse_requirements_txt(filename: str) -> List[str]:
    with open(filename) as fd:
        return list(filter(lambda line: bool(line.strip()), fd.read().splitlines()))


def get_sub_package(packages_path: str) -> str:
    package_cmd = "--package"
    packages = os.listdir(packages_path)
    available_packages = ", ".join(packages)

    if package_cmd not in sys.argv:
        raise RuntimeError(
            f"Specify which package to build with '{package_cmd} <PACKAGE NAME>'. "
            f"Available packages are: {available_packages}"
        )

    index = sys.argv.index(package_cmd)
    sys.argv.pop(index)  # Removes the switch
    package = sys.argv.pop(index)  # Returns the element after the switch
    if package not in packages:
        raise RuntimeError(
            f"Unknown package '{package}'. Available packages are: {available_packages}"
        )
    return package


def get_version(sub_package: str) -> str:
    return importlib.import_module(f"src.{sub_package}").__version__


sources_root = "src"
namespace = "dul"
packages_path = join(sources_root, namespace)
sub_package = get_sub_package(packages_path)
namespaced_package_name = f"{namespace}.{sub_package}"

setup(
    name=namespaced_package_name,
    version=get_version(sub_package),
    description="Dagger Utilities Library",
    author="Daniil Trishkin",
    license="MIT",
    package_dir={"": sources_root},
    packages=find_namespace_packages(
        where=sources_root, include=[namespaced_package_name]
    ),
    include_package_data=True,
    zip_safe=False,
    install_requires=parse_requirements_txt(
        join(packages_path, sub_package, "requirements.txt")
    ),
)
