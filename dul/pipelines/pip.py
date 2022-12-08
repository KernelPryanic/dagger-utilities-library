from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class Actions(Enum):
    INSTALL = "install"
    UNINSTALL = "uninstall"


def _exec(
    container: Container, action: Actions, *packages: str
) -> Container:
    method_name = get_method_name(2)
    if len(packages) == 0:
        log.warning(
            "No packages passed to the module", job=get_job_name(3),
            module=get_module_name(2), method=method_name
        )
        return container

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), action=action.name,
        packages=packages
    )

    return (
        container.
        with_exec(["pip", action.value] + list(packages))
    )


def install(container: Container, packages: list[str]) -> Container:
    return _exec(container, Actions.INSTALL, *packages)


def install(container: Container, packages: list[str]) -> Container:
    return _exec(container, Actions.UNINSTALL, *packages)
