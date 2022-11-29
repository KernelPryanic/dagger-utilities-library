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
        log.info("Mounting source directory", job=get_job_name(), image=image_name, mount=cnt_mnt_dir)
        pipeline = pipeline.with_mounted_directory(cnt_mnt_dir, src_dir)

    return pipeline, cnt_mnt_dir


def get_job_name():
    return inspect.stack()[2][3]

def get_module_name():
    return inspect.stack()[1][3]


# async def preserve_workdir(func: callable):
#     async def wrapper(*args, **kwargs):
#         container = kwargs.get("container")
#         if container is not None:
#             cur_workdir = await container.workdir()
#             c = func(*args, **kwargs)

#             return c.with_workdir(cur_workdir)

#     p = await wrapper
#     return p
