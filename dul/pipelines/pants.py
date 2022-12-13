from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from . import curl
from .cli_helpers import Once, Repeat, Schema
from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class Actions(Enum):
    FORMAT = "fmt"
    LINT = "lint"
    TEST = "test"
    PACKAGE = "package"
    RUN = "run"
    CHECK = "check"


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


argument_schemas = {
    "format": Schema(
        {
            "only": Repeat(repeat("--only"))
        }
    ),
    "lint": Schema(
        {
            "only": Repeat(repeat("--only")),
            "skip_formatters": Once(once("--skip-formatters"))
        }
    ),
    "run": Schema(
        {
            "args": Once(once("--args")),
            "cleanup": Once(once("--cleanup")),
            "debug_adapter": Once(once("--debug-adapter"))
        }
    ),
    "test": Schema(
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
    ),
    "check": Schema(
        {
            "only": Repeat(repeat("--only"))
        }
    )
}


def install(container: Container, root: str = None) -> Container:
    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=get_method_name()
    )

    return (
        curl.get(pipeline, "https://static.pantsbuild.org/setup/pants", output="./pants").
        with_exec(["chmod", "+x", "./pants"])
    )


def _exec(
    container: Container, action: Actions, target: str = "::",
    extra_args: list = [], root: str = None, *args, **kwargs
) -> Container:
    parameters = locals()
    arguments = argument_schemas[get_method_name(
        2)].process(parameters) + extra_args

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=get_method_name(2),
        arguments=arguments
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["./pants", action.value, target] + arguments)
    )


def format(
    container: Container, target: str = "::",
    only: list(Formatters) = None, root: str = None
) -> Container:
    return _exec(container, Actions.FORMAT, locals())


def lint(
    container: Container, target: str = "::",
    only: list(Linters) = None, skip_formatters: bool = False,
    root: str = None
) -> Container:
    return _exec(container, Actions.LINT, locals())


def package(
    container: Container, target: str = "::", root: str = None
) -> Container:
    return _exec(container, Actions.PACKAGE, locals())


def run(
    container: Container, target: str = "::", args: str = None,
    cleanup: bool = None, debug_adapter: bool = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.RUN, locals())


def test(
    container: Container, target: str = "::", debug: bool = None,
    debug_adapter: bool = None, force: bool = None,
    output: TestOuput = None, use_coverage: bool = None,
    open_coverage: bool = None, extra_env_vars: dict = None,
    shard: str = None, test_timeouts: bool = None, root: str = None
) -> Container:
    return _exec(container, Actions.TEST, locals())


def check(
    container: Container, target: str = "::", only: list[str] = None, root: str = None
) -> Container:
    return _exec(container, Actions.CHECK, locals())
