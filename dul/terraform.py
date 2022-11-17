from dagger.api.gen import Client, Container

from .generic import random_string, scripts_dir

import os


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
        with_entrypoint("bash").
        exec([
            os.path.join(mnt_path, "terraform", "docs.sh"),
            "-d", root,
            "-l" if local else ""
        ])
    )


def format(container: Container, root: str) -> Container:
    return (
        container.
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
        exec([
            os.path.join(mnt_path, "terraform", "tfsec.sh"),
            "-d", root
        ])
    )
