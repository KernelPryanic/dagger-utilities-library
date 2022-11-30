import os

from dagger.api.gen import Container

from . import curl


def install(container: Container, version: str):
    return (
        curl.exec(
            container,
            f"https://github.com/aquasecurity/tfsec/releases/download/v{version}/tfsec-linux-amd64",
            options="-sSLotfsec"
        ).
        with_exec(["chmod", "+x", "tfsec"]).
        with_exec(["mv", "tfsec", "/usr/bin/"])
    )


def exec(container: Container, root: str, scripts_path: str) -> Container:
    return (
        container.
        with_entrypoint("bash").
        with_exec([
            os.path.join(scripts_path, "terraform", "tfsec.sh"),
            "-d", root,
        ])
    )
