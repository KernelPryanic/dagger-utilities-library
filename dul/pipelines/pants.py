from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from . import curl
from .generic import (get_job_name, get_method_name, get_module_name,
                      parse_options)

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


options_reflection = {
    "format": {
        "only": "--only"
    },
    "lint": {
        "only": "--only",
        "skip_formatters": "--skip-formatters"
    },
    "run": {
        "args": "--args",
        "cleanup": "--cleanup",
        "debug_adapter": "--debug-adapter"
    },
    "test": {
        "debug": "--debug",
        "debug_adapter": "--debug-adapter",
        "force": "--force",
        "output": "--output",
        "use_coverage": "--use-coverage",
        "open_coverage": "--open-coverage",
        "shard": "--shard",
        "timeouts": "--timeouts"
    },
    "check": {
        "only": "--only"
    }
}


def install(container: Container, root: str = None) -> Container:
    method_name = get_method_name()

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        action=method_name
    )

    return (
        curl.get(pipeline, "https://static.pantsbuild.org/setup/pants", output="./pants").
        with_exec(["chmod", "+x", "./pants"])
    )


def format(
    container: Container, target: str = "::",
    only: list(Formatters) = None, root: str = None
) -> Container:
    arguments = locals()
    options = {}
    method_name = get_method_name()
    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        action=method_name, options=processed_options,
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["./pants", Actions.FORMAT, target] + processed_options)
    )


def lint(
    container: Container, target: str = "::",
    only: list(Linters) = None, skip_formatters: bool = False,
    root: str = None
) -> Container:
    arguments = locals()
    options = {}
    method_name = get_method_name()
    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        action=method_name, options=processed_options,
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["./pants", Actions.LINT, target] + processed_options)
    )


def package(
    container: Container, target: str = "::", root: str = None
) -> Container:
    arguments = locals()
    options = {}
    method_name = get_method_name()
    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        action=method_name, options=processed_options,
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["./pants", Actions.PACKAGE, target] + processed_options)
    )


def run(
    container: Container, target: str = "::", run_args: str = None,
    run_cleanup: bool = None, run_debug_adapter: bool = None, root: str = None
) -> Container:
    arguments = locals()
    options = {}
    method_name = get_method_name()
    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        action=method_name, options=processed_options,
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["./pants", Actions.RUN, target] + processed_options)
    )


def test(
    container: Container, target: str = "::", test_debug: bool = None,
    test_debug_adapter: bool = None, test_force: bool = None,
    test_output: TestOuput = None, test_use_coverage: bool = None,
    test_open_coverage: bool = None, test_extra_env_vars: dict = None,
    test_shard: str = None, test_timeouts: bool = None, root: str = None
) -> Container:
    arguments = locals()
    options = {
        "--test-extra-env-vars": [f"{k}={v}" for k, v in test_extra_env_vars.items()]
    }

    method_name = get_method_name()
    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        action=method_name, options=processed_options,
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["./pants", Actions.TEST, target] + processed_options)
    )


def check(
    container: Container, target: str = "::", only: list[str] = None, root: str = None
) -> Container:
    arguments = locals()
    options = {}
    method_name = get_method_name()
    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        action=method_name, options=processed_options,
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["./pants", Actions.CHECK, target] + processed_options)
    )
