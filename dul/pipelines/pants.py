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
    FAKE = "fake"
    ISORT = "isort"
    SHFMT = "shfmt"


class Linters(Enum):
    FLAKE8 = "flake8"
    SHELLCHECK = "shellcheck"


options_reflection = {
    "format": {
        "only": "--only"
    },
    "lint": {
        "only": "--only",
        "skip_formatters": "--skip_formatters"
    }
}


def install(container: Container, version: str):
    pass


def format(
    container: Container, target: str = "::", only: list(Formatters) = None,
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

    return (
        container.
        with_exec(["./pants", Actions.FORMAT, target] + processed_options)
    )


def lint(
    container: Container, target: str = "::",
    only: list(Linters) = None, skip_formatters: bool = False
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

    return (
        container.
        with_exec(["./pants", Actions.LINT, target] + processed_options)
    )
