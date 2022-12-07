import inspect
import os
import platform
import random
import string

import structlog
from dagger.api.gen import Client, Container, Directory

from dul.scripts.common.structlogging import *

log = structlog.get_logger()

scripts_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "scripts"
)


def random_string(n: int) -> str:
    return "".join(
        random.choices(
            string.ascii_lowercase + string.digits, k=n
        )
    )


def locally() -> bool:
    return platform.system() == "Darwin"


def init(
    client: Client, image_name: str, src_dir: Directory = None
) -> tuple[Container, str]:
    cnt_mnt_dir = f"/{random_string(8)}-src"
    pipeline = (
        client.container().
        from_(image_name)
    )

    log.info("Initializing pipeline", job=get_job_name(), image=image_name)

    if src_dir is not None:
        log.info("Mounting source directory", job=get_job_name(),
                 image=image_name, mount=cnt_mnt_dir)
        pipeline = pipeline.with_mounted_directory(cnt_mnt_dir, src_dir)

    return pipeline, cnt_mnt_dir


async def get_scripts_dir(container: Container) -> str:
    return await container.with_exec(
        "bash", "-c",
        "python -c 'from dul import scripts; from os.path import dirname; print(dirname(pipelines.__file__))'"
    ).stdout()


def get_job_name(level=2):
    return inspect.stack()[level][3]


def get_module_name(level=1):
    return inspect.getmodule(inspect.stack()[level][0]).__name__


def get_method_name(level=1):
    return inspect.stack()[level][3]


def parse_options(
    arguments, options, options_reflection: dict[str, str], method_name: str
) -> list:
    for k, v in arguments.items():
        if v is not None:
            opt = options_reflection[method_name].get(k)
            val = getattr(v, "value", v)
            if opt is not None:
                options[opt] = val

    processed_options = []
    for k, v in options.items():
        if type(v) == list:
            for o in v:
                val = getattr(o, "value", o)
                processed_options.extend([k, val])
        else:
            processed_options.extend([k, v])

    return processed_options


async def preserve_workdir(func: callable, *args, **kwargs):
    a = list(filter(lambda x: type(x) == Container, args))
    pipe = func(*args, **kwargs)
    if len(a) > 0:
        cur_workdir = await a[0].workdir()
        pipe = pipe.with_workdir(cur_workdir)
    return pipe


def _preserve_workdir(func: callable):
    async def wrapper(*args, **kwargs):
        a = list(filter(lambda x: type(x) == Container, args))
        pipe = func(*args, **kwargs)
        if len(a) > 0:
            cur_workdir = await a[0].workdir()
            pipe = pipe.with_workdir(cur_workdir)
        return pipe

    return wrapper
