import structlog

from ..common.dul_exception import DULException
from ..common.structlogging import *
from .cli_helpers import Repeat, Schema, pipe
from .generic import get_job_name, get_method_name

log = structlog.get_logger()


class cli(pipe):
    def __init__(
        self, extra_args: list = []
    ):
        self.schema = Schema(
            {
                "packages": Repeat(lambda v: [v])
            }
        )

        self.cli = ["pip"] + extra_args

    def __common__(
        self, packages: list[str], *args, **kwargs
    ):
        if len(packages) == 0:
            msg = "No packages passed to the module"
            log.error(
                msg, job=get_job_name(3), module=self.__class__.__name__,
                method=get_method_name(2)
            )
            raise DULException(msg)

    def install(self, packages: list[str], extra_args: list = []) -> pipe:
        self.__common__(**locals())
        self.cli += ["install"] + extra_args + self.schema.process(**locals())
        return self

    def uninstall(self, packages: list[str], extra_args: list = []) -> pipe:
        self.__common__(**locals())
        self.cli += ["uninstall"] + extra_args + self.schema.process(**locals())
        return self
