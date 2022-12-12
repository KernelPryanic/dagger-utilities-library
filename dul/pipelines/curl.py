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


argument_schemas = {
    "_exec": Schema(
        {
            "url": Positional(),
            "headers": Repeat("-H", lambda name, k, v: [name, f"{k}: {v}"]),
            "payload": Once("-d", lambda name, v: [name, json.dumps(v)]),
            "redirect": Flag("-L"),
            "silent": Flag("-s"),
            "show_error": Flag("-S"),
            "output": Once("-o")
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
        log.warning(
            "URL is not defined", job=get_job_name(),
            module=get_module_name(), url=url, headers=headers,
            payload=payload
        )
        return container

    parameters = locals()
    method_name = get_method_name(2)
    arguments = []
    exec_arguments += argument_schemas[get_method_name()].process(parameters)
    arguments += argument_schemas[method_name].process(parameters)
    arguments += extra_args

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=get_method_name(2),
        url=url, headers=headers, payload=payload, output=output,
        root=root
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
