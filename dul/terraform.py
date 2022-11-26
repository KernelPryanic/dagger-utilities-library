import os
import sys

from dagger.api.gen import Client, Container

from .generic import random_string, scripts_dir


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
        exec(["-m", "terraform.docs", root] + (["-l"] if local else []))
    )


def format(container: Container, root: str) -> Container:
    return (
        container.
        with_entrypoint("terraform").
        exec(["fmt", "-check", "-recursive", f"{root}"])
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
        exec(["-c", f"ls {mnt_path} && ls {root}"])
        # exec([
        #     os.path.join(mnt_path, "terraform", "tfsec.sh"),
        #     "-d", root,
        # ])
    )
