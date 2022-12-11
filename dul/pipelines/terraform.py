from enum import Enum

from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from . import curl
from .generic import (get_job_name, get_method_name, get_module_name,
                      parse_options)

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


options_reflection = {
    "init": {
        "backend": "-backend",
        "backend_config": "-backend-config",
        "force_copy": "-force-copy",
        "from_module": "-from-module",
        "get": "-get",
        "input": "-input",
        "lock": "-lock",
        "lock_timeout": "-lock-timeout",
        "no_color": "-no-color",
        "plugin_dir": "-plugin-dir",
        "reconfigure": "-reconfigure",
        "migrate_state": "-migrate-state",
        "upgrade": "-upgrade",
        "lockfile": "-lockfile",
        "ignore_remote_version": "-ignore-remote-version"
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
    container: Container, action: Actions, options: dict = {},
    root: str = None, *args, **kwargs
) -> Container:
    arguments = locals()
    method_name = get_method_name(2)
    processed_options = parse_options(
        arguments, options, options_reflection, method_name
    )

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=method_name,
        options=processed_options
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(["terraform", action.value] + processed_options)
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
    pass


def format(container: Container, recursive: bool = None, root: str = None) -> Container:
    return (
        container.
        with_entrypoint("terraform").
        with_exec(["fmt", "-check", "-recursive", f"{root}"])
    )
