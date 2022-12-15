import structlog
from dagger.api.gen import Container

from ..common.structlogging import *
from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


def populate_config(
        container: Container, root: str = None
) -> Container:
    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=get_method_name()
    )

    return (
        pipeline.
        with_exec(
            ["python", "-m", "dul.scripts.atlantis.populate_config", "--check"])
    )
