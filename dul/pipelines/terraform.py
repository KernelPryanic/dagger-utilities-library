from enum import Enum

from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from . import curl
from .cli_helpers import Flag, Once, Schema
from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class Actions(Enum):
    INIT = "init"
    VALIDATE = "validate"
    PLAN = "plan"
    APPLY = "apply"
    DESTROY = "destroy"
    FORMAT = "format"
    SHOW = "show"
    WORKSPACE = "workspace"


class LockfileModes(Enum):
    READONLY = "readonly"


argument_schemas = {
    "init": Schema(
        {
            "backend": Once("-backend"),
            "backend_config": Once("-backend-config"),
            "force_copy": Flag("-force-copy"),
            "from_module": Once("-from-module"),
            "get": Once("-get"),
            "input": Once("-input"),
            "lock": Once("-lock"),
            "lock_timeout": Once("-lock-timeout"),
            "no_color": Flag("-no-color"),
            "plugin_dir": Flag("-plugin-dir"),
            "reconfigure": Flag("-reconfigure"),
            "migrate_state": Flag("-migrate-state"),
            "upgrade": Flag("-upgrade"),
            "lockfile": Once("-lockfile"),
            "ignore_remote_version": Flag("-ignore-remote-version")
        }
    )
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
    container: Container, action: Actions, extra_args: list = [],
    root: str = None,  *args, **kwargs
) -> Container:
    parameters = locals()
    method_name = get_method_name(2)
    arguments = argument_schemas[method_name].process(parameters) + extra_args

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=method_name,
        options=arguments
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["terraform", action.value] + arguments)
    )


def init(
    container: Container, backend: bool = None, backend_config: str = None,
    force_copy: bool = None, from_module: str = None, get: bool = None,
    input: bool = None, lock: bool = None, lock_timeout: int = None,
    no_color: bool = None, plugin_dir: str = None, reconfigure: bool = None,
    migrate_state: bool = None, upgrade: bool = None,
    lockfile: LockfileModes = None, ignore_remote_version: bool = None,
    root: str = None
) -> Container:
    return _exec(container, Actions.INIT, root=root)


def format(container: Container, recursive: bool = None, root: str = None) -> Container:
    return (
        container.
        with_entrypoint("terraform").
        with_exec(["fmt", "-check", "-recursive", f"{root}"])
    )
