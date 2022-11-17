from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="dul",
    version="0.1.0",
    description="Dagger Utilities Library",
    author="Daniil Trishkin",
    license="MIT",
    packages=find_packages(),
    install_requires=required,
    package_data={
        "": ["scripts/**/*"],
    },
)
