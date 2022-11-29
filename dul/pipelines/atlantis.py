from dagger.api.gen import Client, Container

from .generic import random_string, scripts_dir


def populate_config(
        client: Client, container: Container, root: str
) -> Container:
    mnt_path = f"/{random_string(8)}-scripts"

    return (
        container.
        with_mounted_directory(
            mnt_path,
            client.host().
            directory(scripts_dir)
        ).
        with_workdir(root).
        with_env_variable("PYTHONPATH", mnt_path).
        with_entrypoint("python").
        with_exec(["-m", "atlantis.populate_config", "--check"])
    )
