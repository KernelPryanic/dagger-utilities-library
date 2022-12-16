import structlog

from ..common.structlogging import *
from .cli_helpers import Flag, Once, Schema, pipe

log = structlog.get_logger()


def flag(name): return lambda: [name]
def once(name): return lambda value: [name, value]


class scripts(pipe):
    def __init__(self) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "conf": Once(once("--conf")),
                "check": Flag(flag("--check"))
            }
        )

    def update_config(self, conf: str = None, check: bool = None, extra_args: list = []) -> pipe:
        self.cli = (
            ["python", "-m", "dul.scripts.atlantis.update_config"] +
            extra_args +
            self.schema.process(locals())
        )
        return self
