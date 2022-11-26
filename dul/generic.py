import os
import platform
import random
import string

from dagger.api.gen import Client, Container, Directory

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

    if src_dir is not None:
        pipeline = pipeline.with_mounted_directory(cnt_mnt_dir, src_dir)

    return pipeline, cnt_mnt_dir
