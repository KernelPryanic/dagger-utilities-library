import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .generic import get_job_name, get_module_name

log = structlog.get_logger()


def curl(
    container: Container,
    url: str, options: str = ""
) -> Container:

    if len(url) == 0:
        log.warning(
            "URL is not defined",
            job=get_job_name(),
            module=get_module_name(),
            url=url,
            options=options
        )
        return container

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), url=url, options=options
    )

    return (
        container.
        with_exec(["curl", url] + ([options] if len(options) > 0 else []))
    )
