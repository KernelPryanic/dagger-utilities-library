import os
from enum import Enum

from dagger.api.gen import Container

from . import curl
from .cli_helpers import Flag, Once, Positional, Repeat, Schema, pipe


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"


class Format(Enum):
    LOVELY = "lovely"
    JSON = "json"
    CSV = "csv"
    CHECKSTYLE = "checkstyle"
    JUNIT = "junit"
    SARIF = "sarif"
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    GIF = "gif"


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


def flag(name): return lambda: [name]
def once(name): return lambda value: [name, value]
def repeat(name): return once(name)


def list(name):
    return lambda value: [name, ",".join([getattr(v, "value", v) for v in value])]


class cli(pipe):
    def __init__(
        self, target: str = None, code_theme: Theme = None, concise_output: bool = None,
        config_file: str = None, config_file_url: str = None, custom_check_dir: str = None,
        custom_check_url: str = None, debug: bool = None, disable_grouping: bool = None,
        exclude: list[str] = None, exclude_downloaded_modules: bool = None,
        exclude_ignores: list[str] = None, exclude_paths: list[str] = None,
        filter_results: list[str] = None, force_all_dirs: bool = None,
        format: list[Format] = None, ignore_hcl_errors: bool = None, include_ignored: bool = None,
        include_passed: bool = None, migrate_ignores: bool = None,
        minimum_severity: Severity = None, no_code: bool = None, no_color: bool = None,
        no_ignores: bool = None, no_module_downloads: bool = None, out: str = None,
        print_rego_input: bool = None, rego_only: bool = None, rego_policy_dir: str = None,
        run_statistics: bool = None, single_thread: bool = None, soft_fail: bool = None,
        update: bool = None, var_file: str = None, verbose: bool = None, version: bool = None,
        workspace: str = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        schema = Schema(
            {
                "target": Positional(lambda v: v),
                "code_theme": Once(once("--code-theme")),
                "concise_output": Flag(flag("--concise-output")),
                "config_file": Once(once("--config-file")),
                "config_file_url": Once(once("--config-file-url")),
                "custom_check_dir": Once(once("--custom-check-dir")),
                "custom_check_url": Once(once("--custom-check-url")),
                "debug": Flag(flag("--debug")),
                "disable_grouping": Flag(flag("--disable-grouping")),
                "exclude": Once(list("--exclude")),
                "exclude_downloaded_modules": Flag(flag("--exclude-downloaded-modules")),
                "exclude_ignores": Once(list("--exclude-ignores")),
                "exclude_paths": Repeat(repeat("--exclude-path")),
                "filter_results": Once(list("--filter-results")),
                "force_all_dirs": Flag(flag("--force-all-dirs")),
                "format": Once(list("--format")),
                "ignore_hcl_errors": Flag(flag("--ignore-hcl-errors")),
                "include_ignored": Flag(flag("--include-ignored")),
                "include_passed": Flag(flag("--include-passed")),
                "migrate_ignores": Flag(flag("--migrate-ignores")),
                "minimum_severity": Once(once("--minimum-severity")),
                "no_code": Flag(flag("--no-code")),
                "no_color": Flag(flag("--no-color")),
                "no_ignores": Flag(flag("--no-ignores")),
                "no_module_downloads": Flag(flag("--no-module-downloads")),
                "out": Once(once("--out")),
                "print_rego_input": Flag(flag("--print-rego-input")),
                "rego_only": Flag(flag("--rego-only")),
                "rego_policy_dir": Once(once("--rego-policy-dir")),
                "run_statistics": Flag(flag("--run-statistics")),
                "single_thread": Flag(flag("--single-thread")),
                "soft_fail": Flag(flag("--soft-fail")),
                "update": Flag(flag("--update")),
                "var_file": Once(once("--var-file")),
                "verbose": Flag(flag("--verbose")),
                "version": Flag(flag("--version")),
                "workspace": Once(once("--workspace"))
            }
        )
        self.cli = ["tfsec"] + schema.process(parameters) + extra_args

    class __ext(pipe):
        def __init__(self, parent: pipe) -> pipe:
            parameters = locals()
            self.parent = parent
            self.schema = Schema(
                {
                    "target": Positional(lambda v: [v])
                }
            )

        def scan(self, target: str = None, extra_args: list = []) -> pipe:
            self.cli = (
                ["python", "-m", "dul.scripts.terraform.tfsec_scan"] +
                extra_args + ["--command", " ".join(self.parent.cli + [target])] +
                self.schema.process(locals())
            )
            return self

    def ext(self, parent: pipe) -> __ext:
        return self.__ext(self, locals())


def install(container: Container, version: str, root: str = None) -> Container:
    return (
        curl.cli(redirect=True, silent=True, show_error=True, output="tfsec").
        get(f"https://github.com/aquasecurity/tfsec/releases/download/v{version}/tfsec-linux-amd64")(container, root).
        with_exec(["chmod", "+x", "tfsec"]).
        with_exec(["mv", "tfsec", "/usr/local/bin/"])
    )
