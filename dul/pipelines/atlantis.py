from dagger.api.gen import Container


def exec(
        container: Container, root: str
) -> Container:
    return (
        container.
        with_workdir(root).
        with_entrypoint("python").
        with_exec(["-m", "dul.scripts.atlantis.populate_config", "--check"])
    )
