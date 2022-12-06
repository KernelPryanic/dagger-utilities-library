from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class APKActions(Enum):
    INSTALL = "add"
    UNINSTALL = "delete"


def _exec(container: Container, action: APKActions, *packages: str) -> Container:
    if len(packages) == 0:
        log.warning(
            "No packages passed",
            job=get_job_name(3),
            module=get_module_name(2),
            method=get_method_name(2)
        )
        return container

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=get_method_name(2), packages=packages
    )

    return (
        container.
        with_exec(
            ["apk", action.value, "--update", "--no-cache"] + list(packages)
        )
    )


def install(container: Container, packages: list[str]) -> Container:
    return _exec(container, APKActions.INSTALL, *packages)


def uninstall(container: Container, packages: list[str]) -> Container:
    return _exec(container, APKActions.UNINSTALL, *packages)
