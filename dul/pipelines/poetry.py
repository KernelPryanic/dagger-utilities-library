from enum import Enum

from dul.pipelines.base import Flag, Once, Positional, Schema, pipe


def flag(name):
    return lambda: [name]


def once(name):
    return lambda value: [f"{name}={value}"]


def positional():
    return lambda v: [v]


class BuildFormat(Enum):
    SDIST = "sdist"
    WHEEL = "wheel"


class cli(pipe):
    def __init__(
        self,
        quiet: bool = None,
        version: bool = None,
        ansi: bool = None,
        no_ansi: bool = None,
        no_interaction: bool = None,
        no_plugins: bool = None,
        no_cache: bool = None,
        verbose: bool = None,
        extra_args: list = [],
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "quiet": Flag(flag("--quiet")),
                "version": Flag(flag("--version")),
                "ansi": Flag(flag("--ansi")),
                "no_ansi": Flag(flag("--no-ansi")),
                "no_interaction": Flag(flag("--no-interaction")),
                "no_plugins": Flag(flag("--no-plugins")),
                "no_cache": Flag(flag("--no-cache")),
                "verbose": Flag(flag("--verbose")),
                "format": Once(once("--format")),
                "list": Flag(flag("--list")),
                "unset": Flag(flag("--unset")),
                "local": Flag(flag("--local")),
                "key": Positional(positional()),
                "value": Positional(positional()),
                "repository": Once(once("--repository")),
                "username": Once(once("--username")),
                "password": Once(once("--password")),
                "cert": Once(once("--cert")),
                "client_cert": Once(once("--client-cert")),
                "build": Flag(flag("--build")),
                "dry_run": Flag(flag("--dry-run")),
                "skip_existing": Flag(flag("--skip-existing")),
            }
        )
        self.cli = ["poetry"] + self.schema.process(parameters) + extra_args

    def build(self, format: BuildFormat = None, extra_args: list = []) -> pipe:
        self.cli += ["build"] + self.schema.process(locals()) + extra_args
        return self

    def config(
        self, key: str, value: str, list: bool = None, unset: bool = None, local: bool = None, extra_args: list = []
    ) -> pipe:
        self.cli += ["config"] + self.schema.process(locals()) + extra_args
        return self

    def publish(
        self,
        repository: str,
        username: str,
        password: str,
        cert: str = None,
        client_cert: str = None,
        build: bool = None,
        dry_run: bool = None,
        skip_existing: bool = None,
        extra_args: list = [],
    ) -> pipe:
        self.cli += ["publish"] + self.schema.process(locals()) + extra_args
        return self
