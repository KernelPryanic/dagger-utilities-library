import itertools
import json
from enum import Enum

import structlog
from dagger.api.gen import Container

from dul.scripts.common.structlogging import *

from .generic import get_job_name, get_method_name, get_module_name

log = structlog.get_logger()


class CurlActions(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


def _exec(
    container: Container, action: CurlActions, url: str,
    headers: dict = None, payload: dict = None,
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
            ["curl", "-X", action, url] +
            list(itertools.chain([("-X", f"{k}: {v}") for k, v in headers.items()])) +
            (["-d", json.dumps(payload)] if payload is not None else []) +
            ([output] if output is not None else [])
        )
    )


def get(
    container: Container, url: str,
    headers: dict = None, payload: dict = None,
    output: str = None, root: str = None
) -> Container:
    return _exec(container, CurlActions.GET, url, headers, payload, output, root)


def post(
    container: Container, url: str,
    headers: dict = None, payload: dict = None,
    output: str = None, root: str = None
) -> Container:
    return _exec(container, CurlActions.POST, url, headers, payload, output, root)


def put(
    container: Container, url: str,
    headers: dict = None, payload: dict = None,
    output: str = None, root: str = None
) -> Container:
    return _exec(container, CurlActions.PUT, url, headers, payload, output, root)


def patch(
    container: Container, url: str,
    headers: dict = None, payload: dict = None,
    output: str = None, root: str = None
) -> Container:
    return _exec(container, CurlActions.PATCH, url, headers, payload, output, root)


def delete(
    container: Container, url: str,
    headers: dict = None, payload: dict = None,
    output: str = None, root: str = None
) -> Container:
    return _exec(container, CurlActions.DELETE, url, headers, payload, output, root)
