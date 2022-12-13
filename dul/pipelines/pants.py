from enum import Enum

import structlog
from dagger.api.gen import Container

from ..scripts.common.structlogging import *
from .cli_helpers import Once, Repeat, Schema, pipe
from .curl import curl

log = structlog.get_logger()


class Formatters(Enum):
    pass


class Linters(Enum):
    pass


class PyFormatters(Formatters):
    FAKE = "fake"
    BLACK = "black"
    DOCFORMATTER = "docformatter"
    ISORT = "isort"
    YAPF = "yapf"
    AUTOFLAKE = "autoflake"
    PYUPGRADE = "pyupgrade"


class ShellFormatters(Formatters):
    SHFMT = "shfmt"


class ShellLinters(Linters):
    SHELLCHECK = "shellcheck"


class PyLinters(Enum):
    BANDIT = "bandit"
    FLAKE8 = "flake8"
    PYLINT = "pylint"


class TestOuput(Enum):
    ALL = "all"
    FAILED = "failed"
    NONE = "none"


def once(name): return lambda value: [f"{name}={value}"]
def repeat(name): return once(name)


class pants(pipe):
    def __init__(self, target: str = "::", extra_args: list = []):
        parameters = locals()
        schema = Schema(
            {
                "target": Once(lambda v: [v])
            }
        )
        self.cli = ["./pants"] + schema.process(parameters) + extra_args

    def format(self, only: list(Formatters) = None, extra_args: list = []) -> pipe:
        parameters = locals()
        schema = Schema(
            {
                "only": Repeat(repeat("--only"))
            }
        )
        self.cli = ["fmt"] + schema.process(parameters) + extra_args
        return self

    def lint(
        self, only: list(Linters) = None, skip_formatters: bool = False, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        schema = Schema(
            {
                "only": Repeat(repeat("--only")),
                "skip_formatters": Once(once("--skip-formatters"))
            }
        )
        self.cli = ["lint"] + schema.process(parameters) + extra_args
        return self

    def package(
        self, extra_args: list = []
    ) -> pipe:
        self.cli = ["package"] + extra_args
        return self

    def run(
        self, args: str = None, cleanup: bool = None,
        debug_adapter: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        schema = Schema(
            {
                "args": Once(lambda value: [f"--args='{value}'"]),
                "cleanup": Once(once("--cleanup")),
                "debug_adapter": Once(once("--debug-adapter"))
            }
        )
        self.cli = ["run"] + schema.process(parameters) + extra_args
        return self

    def test(
        self, debug: bool = None,
        debug_adapter: bool = None, force: bool = None,
        output: TestOuput = None, use_coverage: bool = None,
        open_coverage: bool = None, extra_env_vars: dict = None,
        shard: str = None, test_timeouts: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        schema = Schema(
            {
                "debug": Once(once("--debug")),
                "debug_adapter": Once(once("--debug-adapter")),
                "force": Once(once("--force")),
                "output": Once(once("--output")),
                "use_coverage": Once(once("--use-coverage")),
                "open_coverage": Once(once("--open-coverage")),
                "extra_env_vars": Repeat(lambda k, v: ["--extra-env-vars", f"{k}={v}"]),
                "shard": Once(once("--shard")),
                "timeouts": Once(once("--timeouts"))
            }
        )
        self.cli = ["test"] + schema.process(parameters) + extra_args
        return self

    def check(
        self, only: list[str] = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        schema = Schema(
            {
                "only": Repeat(repeat("--only"))
            }
        )
        self.cli = ["check"] + schema.process(parameters) + extra_args
        return self


def install(container: Container, root: str = None) -> Container:
    return (
        curl(redirect=True, silent=True, show_error=True, output="./pants").
        get("https://static.pantsbuild.org/setup/pants")(container, root).
        with_exec(["chmod", "+x", "./pants"])
    )
