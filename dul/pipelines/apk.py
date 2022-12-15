import structlog

from ..common.dul_exception import DULException
from ..common.structlogging import *
from .cli_helpers import Flag, Repeat, Schema, pipe
from .generic import get_job_name, get_method_name

log = structlog.get_logger()


def flag(name): return lambda: [name]


class cli(pipe):
    def __init__(
        self, force: bool = None, quite: bool = None,
        update: bool = None, no_cache: bool = None, extra_args: list = []
    ):
        parameters = locals()
        self.schema = Schema(
            {
                "packages": Repeat(lambda v: [v])
            }
        )
        schema = Schema(
            {
                "force": Flag(flag("-f")),
                "quite": Flag(flag("-q")),
                "update": Flag(flag("-U")),
                "no_cache": Flag(flag("--no-cache"))
            }
        )

        self.cli = ["apk"] + extra_args + schema.process(parameters)

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
        self.__common__(locals())
        self.cli += ["add"] + extra_args + self.schema.process(locals())
        return self

    def uninstall(self, packages: list[str], extra_args: list = []) -> pipe:
        self.__common__(locals())
        self.cli += ["del"] + extra_args + self.schema.process(locals())
        return self
