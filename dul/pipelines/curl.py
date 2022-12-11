import itertools
import json
from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class Actions(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


def _exec(
    container: Container, action: Actions, url: str,
    headers: dict = None, payload: dict = None,
    silent: bool = None, show_error: bool = None,
    output: str = None, root: str = None
) -> Container:
    if len(url) == 0:
        log.warning(
            "URL is not defined", job=get_job_name(),
            module=get_module_name(), url=url, headers=headers,
            payload=payload, output=output
        )
        return container

    pipeline = container
    if root is not None:
        pipeline = container.with_workdir(root)

    log.info(
        "Initializing module", job=get_job_name(3),
        module=get_module_name(2), method=get_method_name(2),
        url=url, headers=headers, payload=payload, output=output,
        root=root
    )

    return (
        pipeline.
        with_exec(
            ["curl", "-L", "-X", action, url] +
            list(itertools.chain([("-X", f"{k}: {v}") for k, v in headers.items()])) +
            (["-d", json.dumps(payload)] if payload is not None else []) +
            (["-o", output] if output is not None else []) +
            (["-s"] if silent else []) +
            (["-S"] if show_error else [])
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
        container, Actions.POST, url=url, silent=silent, show_error=show_error,
        headers=headers, payload=payload, root=root
    )


def put(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, payload: dict = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.PUT, url=url, silent=silent, show_error=show_error,
        headers=headers, payload=payload, root=root
    )


def patch(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, payload: dict = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.PATCH, url=url, silent=silent, show_error=show_error,
        headers=headers, payload=payload, root=root
    )


def delete(
    container: Container, url: str,
    silent: bool = False, show_error: bool = False,
    headers: dict = None, root: str = None
) -> Container:
    return _exec(
        container, Actions.DELETE, url=url, silent=silent, show_error=show_error,
        headers=headers, root=root
    )
