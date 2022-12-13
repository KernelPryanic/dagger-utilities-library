import itertools
import json
from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .cli_helpers import Flag, Once, Positional, Repeat, Schema
from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class Actions(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


def flag(name): return lambda: [name]


argument_schemas = {
    "_exec": Schema(
        {
            "url": Positional(lambda v: [f"{v}"]),
            "headers": Repeat(lambda k, v: ["-H", f"{k}: {v}"]),
            "payload": Once(lambda v: ["-d", json.dumps(v)]),
            "redirect": Flag(flag("-L")),
            "silent": Flag(flag("-s")),
            "show_error": Flag(flag("-S")),
            "output": Once(lambda v: ["-o", v])
        }
    ),
    "get": Schema(),
    "post": Schema(),
    "put": Schema(),
    "patch": Schema(),
    "delete": Schema(),
}


def _exec(
    container: Container, action: Actions, url: str,
    headers: dict = None, payload: dict = None,
    redirect: bool = None, silent: bool = None, show_error: bool = None,
    output: str = None, extra_args: list = [], root: str = None
) -> Container:
    if len(url) == 0:
        log.error(
            "URL is not defined", job=get_job_name(3),
            module=get_module_name(2), method=get_method_name(2),
            url=url, headers=headers, payload=payload, root=root
        )
        return container

    parameters = locals()
    arguments = []
    exec_arguments += argument_schemas[get_method_name()].process(parameters)
    arguments += argument_schemas[get_method_name(2)].process(parameters)
    arguments += extra_args

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=get_method_name(2),
        url=url, headers=headers, payload=payload, root=root
    )

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    return (
        pipeline.
        with_exec(
            ["curl", action.value] + exec_arguments + arguments
        )
    )


def get(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, output: str = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.GET, url=url, silent=silent, show_error=show_error,
        headers=headers, output=output, root=root
    )


def post(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, payload: dict = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.POST, locals()
    )


def put(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, payload: dict = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.PUT, locals()
    )


def patch(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, payload: dict = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.PATCH, locals()
    )


def delete(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.DELETE, locals()
    )
