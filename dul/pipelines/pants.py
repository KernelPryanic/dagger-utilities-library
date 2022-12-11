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


argument_schemas = {
    "format": Schema(
        {
            "only": Repeat("--only")
        }
    ),
    "lint": Schema(
        {
            "only": Repeat("--only"),
            "skip_formatters": Once("--skip-formatters")
        }
    ),
    "run": Schema(
        {
            "args": Once("--args"),
            "cleanup": Once("--cleanup"),
            "debug_adapter": Once("--debug-adapter")
        }
    ),
    "test": Schema(
        {
            "debug": Once("--debug"),
            "debug_adapter": Once("--debug-adapter"),
            "force": Once("--force"),
            "output": Once("--output"),
            "use_coverage": Once("--use-coverage"),
            "open_coverage": Once("--open-coverage"),
            "shard": Once("--shard"),
            "timeouts": Once("--timeouts")
        }
    ),
    "check": Schema(
        {
            "only": Repeat("--only")
        }
    )
}


def install(container: Container, root: str = None) -> Container:
    method_name = get_method_name()

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name
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
    method_name = get_method_name(2)
    arguments = argument_schemas[method_name].process(parameters) + extra_args

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=method_name,
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
    return _exec(container, Actions.FORMAT, target=target, root=root, only=only)


def lint(
    container: Container, target: str = "::",
    only: list(Linters) = None, skip_formatters: bool = False,
    root: str = None
) -> Container:
    return _exec(
        container, Actions.LINT, target=target, root=root,
        only=only, skip_formatters=skip_formatters
    )


def package(
    container: Container, target: str = "::", root: str = None
) -> Container:
    return _exec(container, Actions.PACKAGE, target=target, root=root)


def run(
    container: Container, target: str = "::", args: str = None,
    cleanup: bool = None, debug_adapter: bool = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.RUN, target=target, root=root,
        args=args, cleanup=cleanup, debug_adapter=debug_adapter
    )


def test(
    container: Container, target: str = "::", debug: bool = None,
    debug_adapter: bool = None, force: bool = None,
    output: TestOuput = None, use_coverage: bool = None,
    open_coverage: bool = None, extra_env_vars: dict = None,
    shard: str = None, test_timeouts: bool = None, root: str = None
) -> Container:
    extra_args = [
        "--test-extra-env-vars",
        *[f"{k}={v}" for k, v in extra_env_vars.items()]
    ]

    return _exec(
        container, Actions.TEST, target=target, extra_args=extra_args, root=root,
        debug=debug, debug_adapter=debug_adapter, force=force, output=output,
        use_coverage=use_coverage, open_coverage=open_coverage, extra_env_vars=extra_env_vars,
        shard=shard, test_timeouts=test_timeouts
    )


def check(
    container: Container, target: str = "::", only: list[str] = None, root: str = None
) -> Container:
    return _exec(container, Actions.FORMAT, target=target, root=root, only=only)
