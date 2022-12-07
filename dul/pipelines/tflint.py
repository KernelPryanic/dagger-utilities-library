from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from . import curl
from .generic import (get_job_name, get_method_name, get_module_name,
                      parse_options)

log = structlog.get_logger()


class Formats(Enum):
    DEFAULT = "default"
    JSON = "json"
    CHECKSTYLE = "checkstyle"
    JUNIT = "junit"
    COMPACT = "compact"
    SARIF = "sarif"


options_reflection = {
    "exec": {
        "format": "--format",
        "config": "--config",
        "ignore_module": "--ignore-module",
        "enable_rule": "--enable-rule",
        "disable_rule": "--disable-rule",
        "only": "--only",
        "enable_plugin": "--enable-plugin",
        "vars_file": "--var-file",
        "module": "--module",
        "force": "--force",
        "color": "--color"
    }
}


def install(container: Container, version: str):
    binary_name = "tflint"

    return (
        curl.exec(
            container,
            f"https://github.com/terraform-linters/{binary_name}/releases/download/v{version}/tflint_linux_amd64.zip",
            options=f"-sSLo{binary_name}.zip"
        ).
        with_exec(["unzip", f"{binary_name}.zip"]).
        with_exec(["chmod", "+x", binary_name]).
        with_exec(["mv", binary_name, "/usr/bin/"])
    )


def init(container: Container, root: str = None):
    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=get_method_name()
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_workdir(root).
        with_exec(["tflint", "--init"])
    )


def lint(
    container: Container, root: str = None, target: str = "**/*.tf",
    format: Formats = Formats.DEFAULT, config: str = None, ignore_module: str = None,
    enable_rule: str = None, disable_rule: str = None, only: str = None,
    enable_plugin: str = None, vars_file: str = None, vars: dict[str, str] = None,
    module: bool = False, force: bool = False, color: bool = False
) -> Container:
    arguments = locals()
    options = {}
    method_name = get_method_name()

    if vars is not None:
        for k, v in vars.items():
            options.setdefault("--var", [])
            options["--var"].append(f"'{k}={v}'")

    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=method_name,
        options=processed_options,
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["tflint", target] + processed_options)
    )
