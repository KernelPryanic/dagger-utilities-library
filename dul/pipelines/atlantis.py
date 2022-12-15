import structlog

from ..common.structlogging import *
from .cli_helpers import Flag, Once, Schema, pipe

log = structlog.get_logger()


def flag(name): return lambda: [name]
def once(name): return lambda value: [name, value]


class cli(pipe):
    def __init__(self, conf: str = None, check: bool = None, extra_args: list = []):
        parameters = locals()
        schema = Schema(
            {
                "conf": Once(once("--conf")),
                "check": Flag(flag("--check"))
            }
        )
        self.cli = (
            ["python", "-m", "dul.scripts.atlantis.update_config"] +
            schema.process(parameters) + extra_args
        )
