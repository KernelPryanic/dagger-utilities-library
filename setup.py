from os.path import join

from setuptools import find_namespace_packages, setup

with open(join("dul", "common", "requirements.txt")) as f:
    common_requirements = f.read().splitlines()

with open(join("dul", "pipelines", "requirements.txt")) as f:
    pipeline_requirements = f.read().splitlines()

with open(join("dul", "scripts", "requirements.txt")) as f:
    scripts_requirements = f.read().splitlines()

setup(
    name="dul",
    version="0.1.0",
    description="Dagger Utilities Library",
    author="Daniil Trishkin",
    license="MIT",
    packages=find_namespace_packages(),
    install_requires=common_requirements,
    extras_require={
        "pipelines": pipeline_requirements,
        "scripts": scripts_requirements,
    },
    package_data={
        "": ["scripts/**/*.sh"],
    },
)
