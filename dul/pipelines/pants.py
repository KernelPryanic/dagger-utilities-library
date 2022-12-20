from enum import Enum

from dagger.api.gen import Container

from . import curl
from .base import Flag, Once, Positional, Repeat, Schema, pipe


class Formatter(Enum):
    pass


class Linter(Enum):
    pass


class PyFormatter(Formatter):
    FAKE = "fake"
    BLACK = "black"
    DOCFORMATTER = "docformatter"
    ISORT = "isort"
    YAPF = "yapf"
    AUTOFLAKE = "autoflake"
    PYUPGRADE = "pyupgrade"


class BuildFormatter(Formatter):
    BLACK = "black"
    YAPF = "yapf"


class ShellFormatter(Formatter):
    SHFMT = "shfmt"


class ShellLinter(Linter):
    SHELLCHECK = "shellcheck"


class PyLinter(Enum):
    BANDIT = "bandit"
    FLAKE8 = "flake8"
    PYLINT = "pylint"


class TestOuput(Enum):
    ALL = "all"
    FAILED = "failed"
    NONE = "none"


class ChangedDependeesType(Enum):
    NONE = "none"
    DIRECT = "direct"
    TRANSITIVE = "transitive"


def flag(name): return lambda: [name]
def once(name): return lambda value: [f"{name}={value}"]
def repeat(name): return once(name)


class cli(pipe):
    def __init__(self, target: str = None, version: bool = None, extra_args: list = []):
        parameters = locals()
        self.schema = Schema(
            {
                "target": Positional(lambda v: [v]),
                "version": Flag(flag("--version")),
                "since": Once(once("--changed-since")),
                "diffspec": Once(once("--changed-diffspec")),
                "dependees": Once(once("--changed-dependees")),
                "only": Repeat(repeat("--only")),
                "skip_formatters": Once(once("--skip-formatters")),
                "args": Once(lambda value: [f"--args='{value}'"]),
                "cleanup": Once(once("--cleanup")),
                "debug_adapter": Once(once("--debug-adapter")),
                "debug": Once(once("--debug")),
                "force": Once(once("--force")),
                "output": Once(once("--output")),
                "use_coverage": Once(once("--use-coverage")),
                "open_coverage": Once(once("--open-coverage")),
                "extra_env_vars": Repeat(lambda k, v: ["--extra-env-vars", f"{k}={v}"]),
                "shard": Once(once("--shard")),
                "timeouts": Once(once("--timeouts")),
                "check": Once(once("--check")),
                "fmt": Once(once("--fmt")),
                "formatter": Once(once("--formatter")),
                "fix_safe_deprecations":
                Once(once("--fix-safe-deprecations"))
            }
        )
        self.cli = ["./pants"] + self.schema.process(parameters) + extra_args

    def format(self, only: list(Formatter) = None, extra_args: list = []):
        self.cli += ["fmt"] + self.schema.process(locals()) + extra_args
        return self

    def lint(
        self, only: list(Linter) = None, skip_formatters: bool = False, extra_args: list = []
    ):
        self.cli += ["lint"] + self.schema.process(locals()) + extra_args
        return self

    def package(
        self, extra_args: list = []
    ):
        self.cli += ["package"] + extra_args
        return self

    def run(
        self, args: str = None, cleanup: bool = None,
        debug_adapter: bool = None, extra_args: list = []
    ):
        self.cli += ["run"] + self.schema.process(locals()) + extra_args
        return self

    def test(
        self, debug: bool = None,
        debug_adapter: bool = None, force: bool = None,
        output: TestOuput = None, use_coverage: bool = None,
        open_coverage: bool = None, extra_env_vars: dict = None,
        shard: str = None, test_timeouts: bool = None, extra_args: list = []
    ):
        self.cli += ["test"] + self.schema.process(locals()) + extra_args
        return self

    def check(
        self, only: list[str] = None, extra_args: list = []
    ):
        self.cli += ["check"] + self.schema.process(locals()) + extra_args
        return self

    def update_build_files(
        self, check: bool = None, fmt: bool = None, formatter: BuildFormatter = None,
        fix_safe_deprecations: bool = None, extra_args: list = []
    ):
        self.cli += ["update-build-files"] + \
            self.schema.process(locals()) + extra_args
        return self

    def changed(
        self, since: str = None, diffspec: str = None, dependees: ChangedDependeesType = None,
        extra_args: list = []
    ):
        self.cli += self.schema.process(locals()) + extra_args
        return self


def install(container: Container, root: str = None) -> Container:
    return (
        curl.cli(redirect=True, silent=True, show_error=True, output="./pants").
        get("https://static.pantsbuild.org/setup/pants")(container, root).
        with_exec(["chmod", "+x", "./pants"])
    )
