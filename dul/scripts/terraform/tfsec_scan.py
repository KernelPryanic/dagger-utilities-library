import argparse
import os
import subprocess

import anyio
import structlog

from dul.scripts.common import filesystem
from dul.scripts.common.structlogging import *

parser = argparse.ArgumentParser()
parser.add_argument("dir", nargs='?', default=os.getcwd())
parser.add_argument("--command", default="tfsec")
args = parser.parse_args()

log = structlog.get_logger()


async def scan(path: str):
    command = args.command.split(' ')

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    if output != b"":
        log.info(output, path=path)
    if error != b"":
        log.error(error, path=path)
        raise SystemExit(1)


async def main():
    async with anyio.create_task_group() as tg:
        for path in filesystem.find_files(args.dir, "main.tf"):
            tg.start_soon(scan, os.path.dirname(path))

if __name__ == "__main__":
    anyio.run(main)
