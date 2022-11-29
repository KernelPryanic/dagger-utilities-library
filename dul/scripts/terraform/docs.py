import argparse
import os
import subprocess

import anyio
import structlog
from dul.scripts.common.structlogging import *
from dul.scripts.common import filesystem

parser = argparse.ArgumentParser()
parser.add_argument("dir", nargs='?', default=os.getcwd())
parser.add_argument("-l", "--local", action='store_true')
args = parser.parse_args()

log = structlog.get_logger()

readme_name = "README.md"


async def docs(path: str, local: bool):
    command = f"terraform-docs markdown table --output-file {readme_name} --output-mode inject"

    def generate_readme():
        process = subprocess.Popen(
            command.split() + [path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()
        if output != b"":
            log.info(output, path=path)
        if error != b"":
            log.error(error, path=path)
            raise SystemExit(1)

    if local:
        generate_readme()
    else:
        readme = os.path.join(path, readme_name)
        if not os.path.exists(readme):
            log.error(
                f"File {readme} doesn't exist",
                hint=f"Try running {command} {path}"
            )
            raise SystemExit(1)
        else:
            with open(readme, 'r') as file:
                current_readme = file.read()
            generate_readme()
            with open(readme, 'r') as file:
                new_readme = file.read()

            if current_readme != new_readme:
                log.error(
                    f"File {readme} doesn't seem to be up-to-date.",
                    hint=f"Try running {command} {path}"
                )
                raise SystemExit(1)


async def main():
    async with anyio.create_task_group() as tg:
        for path in filesystem.find_files(args.dir, "main.tf"):
            tg.start_soon(docs, os.path.dirname(path), args.local)

if __name__ == "__main__":
    anyio.run(main)
