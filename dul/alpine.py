from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .generic import get_job_name, get_module_name

log = structlog.get_logger()


class APKActions(Enum):
    INSTALL = "add"
    UNINSTALL = "delete"


def apk(
    container: Container,
    action: APKActions, *packages: str
) -> Container:

    if len(packages) == 0:
        log.warning(
            "No packages passed to the module",
            job=get_job_name(),
            module=get_module_name(),
            action=action.name
        )
        return container

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), action=action.name, packages=packages
    )

    return (
        container.
        with_exec(["apk", action.value, "--update", "--no-cache"] + list(packages))
    )
