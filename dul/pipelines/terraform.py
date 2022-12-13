from enum import Enum

from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from . import curl
from .cli_helpers import Flag, Once, Repeat, Schema
from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class Actions(Enum):
    VERSION = "-version"
    INIT = "init"
    VALIDATE = "validate"
    PLAN = "plan"
    APPLY = "apply"
    DESTROY = "destroy"
    FORMAT = "fmt"
    SHOW = "show"
    WORKSPACE = "workspace"


class LockfileModes(Enum):
    READONLY = "readonly"


def flag(name): return lambda: [name]
def once(name): return lambda value: [f"{name}={value}"]


argument_schemas = {
    "_exec": Schema(
        {
            "chdir": Once("-chdir")
        }
    ),
    "version": Schema(),
    "init": Schema(
        {
            "backend": Once(once("-backend")),
            "backend_config": Once(once("-backend-config")),
            "force_copy": Flag(flag("-force-copy")),
            "from_module": Once(once("-from-module")),
            "get": Once(once("-get")),
            "input": Once(once("-input")),
            "lock": Once(once("-lock")),
            "lock_timeout": Once(once("-lock-timeout")),
            "no_color": Flag(flag("-no-color")),
            "plugin_dir": Flag(flag("-plugin-dir")),
            "reconfigure": Flag(flag("-reconfigure")),
            "migrate_state": Flag(flag("-migrate-state")),
            "upgrade": Flag(flag("-upgrade")),
            "lockfile": Once(once("-lockfile")),
            "ignore_remote_version": Flag(flag("-ignore-remote-version"))
        }
    ),
    "validate": Schema(
        {
            "json": Flag(flag("-json")),
            "no-color": Flag(flag("-no-color"))
        }
    ),
    "plan": Schema(
        {
            "destroy": Flag(flag("-destroy")),
            "refresh_only": Flag(flag("-refresh-only")),
            "refresh": Once(once("-refresh")),
            "replace": Once(once("-replace")),
            "target": Once(once("-target")),
            "vars": Repeat(lambda k, v: ["-var", f"{k}={v}"]),
            "var_file": Once(once("-var-file")),
            "compact_warnings": Flag(flag("-compact-warnings")),
            "detailed_exitcode": Flag(flag("-detailed-exitcode")),
            "input": Once(once("-input")),
            "lock": Once(once("-lock")),
            "lock_timeout": Once(once("-lock-timeout")),
            "no_color": Flag(flag("-no-color")),
            "out": Once(once("-out")),
            "parallelism": Once(once("-parallelism")),
            "state": Once(once("-state"))
        }
    ),
    "apply": Schema(
        {
            "auto_approve": Flag(flag("-auto-approve")),
            "backup": Once(once("-backup")),
            "compact_warnings": Flag(flag("-compact-warnings")),
            "destroy": Flag(flag("-destroy")),
            "lock": Once(once("-lock")),
            "lock_timeout": Once(once("-lock-timeout")),
            "input": Once(once("-input")),
            "no_color": Flag(flag("-no-color")),
            "parallelism": Once(once("-parallelism")),
            "state": Once(once("-state")),
            "state_out": Once(once("-state-out"))
        }
    ),
    "destroy": Schema(
        {
            "auto_approve": Flag(flag("-auto-approve")),
            "backup": Once(once("-backup")),
            "compact_warnings": Flag(flag("-compact-warnings")),
            "lock": Once(once("-lock")),
            "lock_timeout": Once(once("-lock-timeout")),
            "input": Once(once("-input")),
            "no_color": Flag(flag("-no-color")),
            "parallelism": Once(once("-parallelism")),
            "state": Once(once("-state")),
            "state_out": Once(once("-state-out"))
        }
    ),
    "format": Schema(
        {
            "list": Once(once("-list")),
            "write": Once(once("-write")),
            "diff": Flag(flag("-diff")),
            "check": Flag(flag("-check")),
            "no_color": Flag(flag("-no-color")),
            "recursive": Flag(flag("-recursive"))
        }
    ),
    "show": Schema(
        {
            "no_color": Flag(flag("-no-color")),
            "json": Flag(flag("-json"))
        }
    ),
    "workspace": {
        "delete": Schema(),
        "list": Schema(),
        "new": Schema(),
        "select": Schema(),
        "show": Schema()
    }
}


def install(container: Container, version: str):
    return (
        curl.get(
            container,
            f"https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_amd64.zip",
            silent=True, show_error=True, output="terraform.zip"
        ).
        with_exec(["unzip", "terraform.zip"]).
        with_exec(["chmod", "+x", "terraform"]).
        with_exec(["mv", "terraform", "/usr/local/bin/"])
    )


def _exec(
    container: Container, action: Actions,
    chdir: str = None, extra_args: list = [],
    root: str = None,  *args, **kwargs
) -> Container:
    parameters = locals()
    arguments = []
    exec_arguments += argument_schemas[get_method_name()].process(parameters)
    arguments += argument_schemas[get_method_name(2)].process(parameters)
    arguments += extra_args

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=get_method_name(2),
        options=arguments
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(
            ["terraform"] + exec_arguments + [action.value] + arguments
        )
    )


def version(container: Container) -> Container:
    return _exec(container, Actions.VERSION)


def init(
    container: Container, backend: bool = None, backend_config: str = None,
    force_copy: bool = None, from_module: str = None, get: bool = None,
    input: bool = None, lock: bool = None, lock_timeout: int = None,
    no_color: bool = None, plugin_dir: str = None, reconfigure: bool = None,
    migrate_state: bool = None, upgrade: bool = None,
    lockfile: LockfileModes = None, ignore_remote_version: bool = None,
    root: str = None, *args, **kwargs
) -> Container:
    return _exec(container, Actions.INIT, locals())


def validate(
    container: Container, json: bool = None, no_color: bool = None,
    root: str = None, *args, **kwargs
) -> Container:
    return _exec(container, Actions.VALIDATE, locals())


def plan(
    container: Container, destroy: bool = None, refresh_only: bool = None,
    refresh: bool = None, replace: str = None, target: str = None,
    vars: dict = None, var_file: str = None, compact_warnings: bool = None,
    detailed_exitcode: bool = None, input: bool = None, lock: bool = None,
    lock_timeout: str = None, no_color: bool = None, out: str = None,
    parallelism: int = None, state: str = None,
    root: str = None, *args, **kwargs
) -> Container:
    return _exec(container, Actions.PLAN, locals())


def apply(
    container: Container, auto_approve: bool = None, backup: str = None,
    compact_warnings: bool = None, destroy: bool = None, lock: bool = None,
    lock_timeout: str = None, input: bool = None, no_color: bool = None,
    parallelism: int = None, state: str = None, state_out: str = None,
    root: str = None, *args, **kwargs
) -> Container:
    return _exec(container, Actions.APPLY, locals())


def destroy(
    container: Container, auto_approve: bool = None, backup: str = None,
    compact_warnings: bool = None, lock: bool = None,
    lock_timeout: str = None, input: bool = None, no_color: bool = None,
    parallelism: int = None, state: str = None, state_out: str = None,
    root: str = None, *args, **kwargs
) -> Container:
    return _exec(container, Actions.DESTROY, locals())


def format(
    container: Container, list: bool = None, write: bool = None,
    diff: bool = None, check: bool = None, no_color: bool = None,
    recursive: bool = None, root: str = None
) -> Container:
    return _exec(container, Actions.FORMAT, locals())


def show(
    container: Container, no_color: bool = None,
    json: bool = None, root: str = None
) -> Container:
    return _exec(container, Actions.SHOW, locals())
