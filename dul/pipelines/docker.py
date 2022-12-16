from enum import Enum

from .cli_helpers import Flag, Once, Positional, Repeat, Schema, pipe


def flag(name): return lambda: [name]
def once(name): return lambda value: [name, value]
def repeat(name): return once(name)
def positional(): return lambda v: [v]


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


class cli(pipe):
    def __init__(
        self, config: str = None, context: str = None, debug: bool = None,
        hosts: list[str] = None, log_level: LogLevel = None, tls: bool = None,
        tlscacert: str = None, tlscert: str = None, tlskey: str = None,
        tlsverify: bool = None, version: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "path": Positional(positional()),
                "name": Positional(positional()),
                "config": Once(once("--config")),
                "context": Once(once("--context")),
                "debug": Flag(flag("--debug")),
                "host": Repeat(repeat("--host")),
                "log_level": Once(once("--log-level")),
                "tls": Flag(flag("--tls")),
                "tlscacert": Once(once("--tlscacert")),
                "tlscert": Once(once("--tlscert")),
                "tlskey": Once(once("--tlskey")),
                "tlsverify": Flag(flag("--tlsverify")),
                "version": Flag(flag("--version")),
                "add_hosts": Repeat(repeat("--add-host")),
                "build_args": Repeat(repeat("--build-arg")),
                "cache_from": Repeat(repeat("--cache-from")),
                "disable_content_trust": Flag(flag("--disable-content-trust")),
                "file": Once(once("--file")),
                "iidfile": Once(once("--iidfile")),
                "isolation": Once(once("--isolation")),
                "labels": Repeat(repeat("--label")),
                "network": Once(once("--network")),
                "no_cache": Flag(flag("--no-cache")),
                "output": Once(once("--output")),
                "platform": Once(once("--platform")),
                "progress": Once(once("--progress")),
                "pull": Flag(flag("--pull")),
                "quiet": Flag(flag("--quiet")),
                "secret": Once(once("--secret")),
                "ssh": Once(once("--ssh")),
                "tags": Repeat(repeat("--tag")),
                "target": Once(once("--target")),
                "all_tags": Flag(flag("--all-tags"))
            }
        )
        self.cli = ["docker"] + extra_args + \
            self.schema.process(**parameters)

    def build(
        self, add_hosts: list[str] = None, build_args: list[str] = None,
        cache_from: list[str] = None, disable_content_trust: bool = None,
        file: str = None, iidfile: str = None, isolation: str = None,
        labels: list[str] = None, network: str = None, no_cache: bool = None,
        output: str = None, platform: str = None, progress: str = None, pull: bool = None,
        quiet: bool = None, secret: str = None, ssh: str = None, tags: list[str] = None,
        target: str = None, path: str = None, extra_args: list = []
    ) -> pipe:
        self.cli += ["build"] + extra_args + self.schema.process(**locals())
        return self

    def push(
        self, all_tags: bool = None, disable_content_trust: bool = None,
        quiet: bool = None, name: str = None, extra_args: list = []
    ) -> pipe:
        self.cli += ["push"] + extra_args + self.schema.process(**locals())
        return self

    class __login(pipe):
        def __init__(
            self, parent: pipe, *args, **kwargs
        ) -> pipe:
            parameters = locals()
            self.schema = Schema(
                {
                    "username": Once(once("--username")),
                    "password": Once(once("--password")),
                    "client_id": Once(once("--client-id")),
                    "client_secret": Once(once("--client-secret")),
                    "cloud_name": Once(once("--cloud-name")),
                    "tenant_id": Once(once("--tenant-id"))
                }
            )
            self.cli = parent.cli + ["login"] + \
                kwargs["extra_args"] + self.schema.process(**parameters)

        def azure(
            self, client_id: str = None, client_secret: str = None, cloud_name: str = None,
            tenant_id: str = None, extra_args: list = []
        ) -> pipe:
            self.cli += ["azure"] + \
                extra_args + self.schema.process(**locals())
            return self

    def login(
        self, username: str = None, password: str = None,
        server: str = None, extra_args: list = []
    ) -> __login:
        return self.__login(self, **locals())
