from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from . import curl
from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class Actions(Enum):
    LINT = ""
    INIT = "--init"


class Formats(Enum):
    DEFAULT = "default"
    JSON = "json"
    CHECKSTYLE = "checkstyle"
    JUNIT = "junit"
    COMPACT = "compact"
    SARIF = "sarif"


class OptionsReflection(Enum):
    format = "--format"
    config = "--config"
    ignore_module = "--ignore-module"
    enable_rule = "--enable-rule"
    disable_rule = "--disable-rule"
    only = "--only"
    enable_plugin = "--enable-plugin"
    vars_file = "--var-file"
    module = "--module"
    force = "--force"
    color = "--color"


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


def exec(
    container: Container, action: Actions = Actions.LINT, target: str = "**/*.tf",
    format: Formats = Formats.DEFAULT, config: str = None, ignore_module: str = None,
    enable_rule: str = None, disable_rule: str = None, only: str = None,
    enable_plugin: str = None, vars_file: str = None, vars: dict[str, str] = None,
    module: bool = False, force: bool = False, color: bool = False
) -> Container:
    arguments = locals()
    options = {}

    for k, v in arguments.items():
        if v is not None:
            opt = getattr(OptionsReflection, k, None)
            val = getattr(v, "value", v)
            if opt is not None:
                options[opt.value] = val

    if vars is not None:
        for k, v in vars.items():
            options.setdefault("--var", [])
            options["--var"].append(f"'{k}={v}'")

    processed_options = []
    for k, v in options.items():
        if type(v) == list:
            for o in v:
                processed_options.extend([k, o])
        else:
            processed_options.extend([k, v])

    log.info(
        "Initializing module", job=get_job_name(),
        module=get_module_name(), method=get_method_name(),
        action=action.name, options=processed_options,
    )

    return (
        container.
        with_exec(["tflint", action.value, target] + processed_options)
    )
