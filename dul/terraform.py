import os

from dagger.api.gen import Client, Container

from .generic import random_string, scripts_dir
from .http import curl


def install(container: Container, version: str):
    return (
        curl(
            container,
            f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_amd64.zip",
            options="-sSLoterraform.zip"
        ).
        with_exec(["unzip", "terraform.zip"]).
        with_exec(["chmod", "+x", "terraform"]).
        with_exec(["mv", "terraform", "/usr/bin/"])
    )


def install_tfsec(container: Container, version: str):
    return (
        curl(
            container,
            f"https://github.com/aquasecurity/tfsec/releases/download/v{version}/tfsec-linux-amd64",
            options="-sSLotfsec"
        ).
        with_exec(["chmod", "+x", "tfsec"]).
        with_exec(["mv", "tfsec", "/usr/bin/"])
    )


def install_docs(container: Container, version: str):
    return (
        curl(
            container,
            f"https://terraform-docs.io/dl/v{version}/terraform-docs-v{version}-linux-amd64.tar.gz",
            options="-sSLoterraform-docs.tar.gz"
        ).
        with_exec(["tar", "-xzf", "terraform-docs.tar.gz"]).
        with_exec(["chmod", "+x", "terraform-docs"]).
        with_exec(["mv", "terraform-docs", "/usr/bin/"])
    )


def docs(
        client: Client, container: Container,
        root: str, local: bool = False,
) -> Container:
    mnt_path = f"/{random_string(8)}-scripts"

    return (
        container.
        with_mounted_directory(
            mnt_path,
            client.host().
            directory(scripts_dir)
        ).
        with_env_variable("PYTHONPATH", mnt_path).
        with_entrypoint("python").
        with_exec(["-m", "terraform.docs", root] + (["-l"] if local else []))
    )


def format(container: Container, root: str) -> Container:
    return (
        container.
        with_entrypoint("terraform").
        with_exec(["fmt", "-check", "-recursive", f"{root}"])
    )


def tfsec(client: Client, container: Container, root: str) -> Container:
    mnt_path = f"/{random_string(8)}-scripts"

    return (
        container.
        with_mounted_directory(
            mnt_path,
            client.host().
            directory(scripts_dir)
        ).
        with_entrypoint("bash").
        with_exec([
            os.path.join(mnt_path, "terraform", "tfsec.sh"),
            "-d", root,
        ])
    )
