from enum import Enum

import structlog
from dagger.api.gen import Container

from ..common.structlogging import *
from . import curl
from .cli_helpers import Flag, Once, Positional, Repeat, Schema, pipe

log = structlog.get_logger()


class Format(Enum):
    DEFAULT = "default"
    JSON = "json"
    CHECKSTYLE = "checkstyle"
    JUNIT = "junit"
    COMPACT = "compact"
    SARIF = "sarif"


def flag(name): return lambda: [name]
def once(name): return lambda value: [f"{name}={value}"]
def repeat(name): return once(name)


class tflint(pipe):
    def __init__(
        self, version: bool = None, init: bool = None, format: Format = None,
        config: str = None, ignore_module: str = None, enable_rule: str = None,
        disable_rule: str = None, only: list[str] = None, enable_plugin: str = None,
        var_file: str = None, vars: dict = None, module: bool = None, force: bool = None,
        color: bool = None, no_color: bool = None, target: str = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        schema = Schema(
            {
                "target": Positional(lambda v: [v]),
                "version": Flag(flag("-v")),
                "init": Flag(flag("--init")),
                "format": Once(once("-f")),
                "config": Once(once("-c")),
                "ignore_module": Once(once("--ignore-module")),
                "enable_rule": Once(once("--enable-rule")),
                "disable_rule": Once(once("--disable-rule")),
                "only": Repeat(repeat("--only")),
                "enable_plugin": Once(once("--enable-plugin")),
                "var_file": Once(once("--var-file")),
                "vars": Repeat(lambda k, v: ["-var", f"{k}={v}"]),
                "module": Flag(flag("--module")),
                "force": Flag(flag("--force")),
                "color": Flag(flag("--color")),
                "no_color": Flag(flag("--no-color"))
            }
        )
        self.cli = ["tflint"] + extra_args + schema.process(**parameters)


def install(container: Container, version: str, root: str = None):
    binary_name = "tflint"
    return (
        curl.cli(redirect=True, silent=True, show_error=True, output="tfsec").
        get(f"https://github.com/terraform-linters/{binary_name}/releases/download/v{version}/tflint_linux_amd64.zip")(container, root).
        with_exec(["unzip", f"{binary_name}.zip"]).
        with_exec(["chmod", "+x", binary_name]).
        with_exec(["mv", binary_name, "/usr/bin/"])
    )
