from enum import Enum

from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .cli_helpers import Flag, Once, Repeat, Schema, pipe
from .curl import curl

log = structlog.get_logger()


class LockfileMode(Enum):
    READONLY = "readonly"


def flag(name): return lambda: [name]
def once(name): return lambda value: [f"{name}={value}"]


class cli(pipe):
    def __init__(
        self, version: bool = None, chdir: str = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "version": Flag(flag("-version")),
                "chdir": Once(once("-chdir")),
                "no_color": Flag(flag("-no-color")),
                "backend": Once(once("-backend")),
                "backend_config": Once(once("-backend-config")),
                "force_copy": Flag(flag("-force-copy")),
                "from_module": Once(once("-from-module")),
                "get": Once(once("-get")),
                "input": Once(once("-input")),
                "lock": Once(once("-lock")),
                "lock_timeout": Once(once("-lock-timeout")),
                "plugin_dir": Flag(flag("-plugin-dir")),
                "reconfigure": Flag(flag("-reconfigure")),
                "migrate_state": Flag(flag("-migrate-state")),
                "upgrade": Flag(flag("-upgrade")),
                "lockfile": Once(once("-lockfile")),
                "ignore_remote_version": Flag(flag("-ignore-remote-version")),
                "destroy": Flag(flag("-destroy")),
                "refresh_only": Flag(flag("-refresh-only")),
                "refresh": Once(once("-refresh")),
                "replace": Once(once("-replace")),
                "target": Once(once("-target")),
                "vars": Repeat(lambda k, v: ["-var", f"{k}={v}"]),
                "var_file": Once(once("-var-file")),
                "compact_warnings": Flag(flag("-compact-warnings")),
                "detailed_exitcode": Flag(flag("-detailed-exitcode")),
                "lock": Once(once("-lock")),
                "out": Once(once("-out")),
                "parallelism": Once(once("-parallelism")),
                "state": Once(once("-state")),
                "json": Flag(flag("-json")),
                "auto_approve": Flag(flag("-auto-approve")),
                "backup": Once(once("-backup")),
                "state_out": Once(once("-state-out")),
                "list": Once(once("-list")),
                "write": Once(once("-write")),
                "diff": Flag(flag("-diff")),
                "check": Flag(flag("-check")),
                "recursive": Flag(flag("-recursive"))
            }
        )
        self.cli = ["terraform"] + extra_args + self.schema.process(parameters)

    def init(
        self, backend: bool = None, backend_config: str = None,
        force_copy: bool = None, from_module: str = None, get: bool = None,
        input: bool = None, lock: bool = None, lock_timeout: int = None,
        no_color: bool = None, plugin_dir: str = None, reconfigure: bool = None,
        migrate_state: bool = None, upgrade: bool = None,
        lockfile: LockfileMode = None, ignore_remote_version: bool = None,
        extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.cli += ["init"] + extra_args + self.schema.process(parameters)
        return self

    def validate(
        self, json: bool = None, no_color: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.cli += ["validate"] + extra_args + self.schema.process(parameters)
        return self

    def plan(
        self, destroy: bool = None, refresh_only: bool = None,
        refresh: bool = None, replace: str = None, target: str = None,
        vars: dict = None, var_file: str = None, compact_warnings: bool = None,
        detailed_exitcode: bool = None, input: bool = None, lock: bool = None,
        lock_timeout: str = None, no_color: bool = None, out: str = None,
        parallelism: int = None, state: str = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.cli += ["plan"] + extra_args + self.schema.process(parameters)
        return self

    def apply(
        self, auto_approve: bool = None, backup: str = None,
        compact_warnings: bool = None, destroy: bool = None, lock: bool = None,
        lock_timeout: str = None, input: bool = None, no_color: bool = None,
        parallelism: int = None, state: str = None, state_out: str = None,
        extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.cli += ["apply"] + extra_args + self.schema.process(parameters)
        return self

    def destroy(
        self, auto_approve: bool = None, backup: str = None,
        compact_warnings: bool = None, lock: bool = None,
        lock_timeout: str = None, input: bool = None, no_color: bool = None,
        parallelism: int = None, state: str = None, state_out: str = None,
        extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.cli += ["destroy"] + extra_args + self.schema.process(parameters)
        return self

    def format(
        self, list: bool = None, write: bool = None,
        diff: bool = None, check: bool = None, no_color: bool = None,
        recursive: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.cli += ["format"] + extra_args + self.schema.process(parameters)
        return self

    def show(
        self, json: bool = None, no_color: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.cli += ["show"] + extra_args + self.schema.process(parameters)
        return self

    class __workspace(pipe):
        def __init__(self, parent: pipe, extra_args: list = []) -> pipe:
            self.schema = {
                "force": Flag(flag("-force")),
                "lock": Once(once("-lock")),
                "lock_timeout": Once(once("-lock-timeout")),
                "state": Once(once("-state"))
            }
            self.cli = parent.cli + ["workspace"] + extra_args

        def delete(
            self, force: bool = None, lock: bool = None,
            lock_timeout: str = None, extra_args: list = []
        ) -> pipe:
            self.cli += ["delete"] + extra_args + \
                self.schema.process(locals())
            return self

        def list(self, extra_args: list = []) -> pipe:
            self.cli += ["list"] + extra_args
            return self

        def new(self, extra_args: list = []) -> pipe:
            self.cli += ["new"] + extra_args + self.schema.process(locals())
            return self

        def select(self, extra_args: list = []) -> pipe:
            self.cli += ["select"] + extra_args
            return self

        def show(self, extra_args: list = []) -> pipe:
            self.cli += ["select"] + extra_args
            return self

    def workspace(
        self, extra_args: list = []
    ) -> __workspace:
        return self.__workspace(self, locals())


def install(container: Container, version: str, root: str = None) -> Container:
    return (
        curl(redirect=True, silent=True, show_error=True, output="./pants").
        get(f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_amd64.zip")(container, root).
        with_exec(["unzip", "terraform.zip"]).
        with_exec(["chmod", "+x", "terraform"]).
        with_exec(["mv", "terraform", "/usr/local/bin/"])
    )
