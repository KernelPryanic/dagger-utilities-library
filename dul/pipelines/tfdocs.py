from dagger.api.gen import Container

from . import curl


def install(container: Container, version: str):
    return (
        curl.exec(
            container,
            f"https://terraform-docs.io/dl/v{version}/terraform-docs-v{version}-linux-amd64.tar.gz",
            options="-sSLoterraform-docs.tar.gz"
        ).
        with_exec(["tar", "-xzf", "terraform-docs.tar.gz"]).
        with_exec(["chmod", "+x", "terraform-docs"]).
        with_exec(["mv", "terraform-docs", "/usr/bin/"])
    )


def exec(
        container: Container,
        root: str, local: bool = False,
) -> Container:
    return (
        container.
        with_entrypoint("python").
        with_exec(["-m", "dul.scripts.terraform.docs", root] + (["-l"] if local else []))
    )
