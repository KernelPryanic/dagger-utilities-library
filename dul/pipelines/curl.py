import json

import structlog

from ..common.dul_exception import DULException
from ..scripts.common.structlogging import *
from .cli_helpers import Flag, Once, Positional, Repeat, Schema, pipe
from .generic import get_job_name, get_method_name

log = structlog.get_logger()


def flag(name): return lambda: [name]


class cli(pipe):
    def __init__(
        self, redirect: bool = None, silent: bool = None,
        show_error: bool = None, output: str = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "url": Positional(lambda v: [v]),
                "headers": Repeat(lambda k, v: ["-H", f"{k}: {v}"]),
                "payload": Once(lambda v: ["-d", json.dumps(v)])
            }
        )
        schema = Schema(
            {
                "redirect": Flag(flag("-L")),
                "silent": Flag(flag("-s")),
                "show_error": Flag(flag("-S")),
                "output": Once(lambda v: ["-o", v])
            }
        )
        self.cli = ["curl"] + extra_args + schema.process(parameters)

    def __common__(
        self, url: str, headers: dict = None, payload: dict = None,
        *args, **kwargs
    ):
        if len(url) == 0:
            msg = "URL is not defined"
            log.error(
                msg, job=get_job_name(3),
                module=self.__class__.__name__, method=get_method_name(2),
                url=url, headers=headers, payload=payload
            )
            raise DULException(msg)

    def get(
        self, url: str, headers: dict = None, payload: dict = None,
        extra_args: list = []
    ) -> pipe:
        self.__common__(locals())
        self.cli += ["-X", "GET"] + extra_args + self.schema.process(locals())
        return self

    def post(
        self, url: str, headers: dict = None, payload: dict = None,
        extra_args: list = []
    ) -> pipe:
        self.__common__(locals())
        self.cli += ["-X", "POST"] + extra_args + self.schema.process(locals())
        return self

    def put(
        self, url: str, headers: dict = None, payload: dict = None,
        extra_args: list = []
    ) -> pipe:
        self.__common__(locals())
        self.cli += ["-X", "PUT"] + extra_args + self.schema.process(locals())
        return self

    def patch(
        self, url: str, headers: dict = None, payload: dict = None,
        extra_args: list = []
    ) -> pipe:
        self.__common__(locals())
        self.cli += ["-X", "PATCH"] + extra_args + \
            self.schema.process(locals())
        return self

    def delete(
        self, url: str, headers: dict = None, payload: dict = None,
        extra_args: list = []
    ) -> pipe:
        self.__common__(locals())
        self.cli += ["-X", "DELETE"] + extra_args + \
            self.schema.process(locals())
        return self
