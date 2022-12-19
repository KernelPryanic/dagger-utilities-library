from enum import Enum

from .base import Flag, Once, Positional, Schema, pipe


class Theme(Enum):
    MKDOCS = "mkdocs"
    READTHEDOCS = "readthedocs"


def flag(name): return lambda: [name]
def once(name): return lambda value: [name, value]


class cli(pipe):
    def __init__(
        self, version: bool = None, quiet: bool = None,
        verbose: bool = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "target": Positional(lambda v: [v]),
                "version": Flag(flag("--version")),
                "quiet": Flag(flag("--quiet")),
                "verbose": Flag(flag("--verbose")),
                "clean": Flag(flag("--clean")),
                "dirty": Flag(flag("--dirty")),
                "config_file": Once(once("--config-file")),
                "strict": Flag(flag("--strict")),
                "theme": Once(once("--theme")),
                "use_directory_urls": Flag(flag("--use-directory-urls")),
                "no_directory_urls": Flag(flag("--no-directory-urls")),
                "site_dir": Once(once("--site-dir")),
                "message": Once(once("--message")),
                "remote_branch": Once(once("--remote-branch")),
                "remote_name": Once(once("--remote-name")),
                "force": Flag(flag("--force")),
                "no_history": Flag(flag("--no-history")),
                "ignore_version": Flag(flag("--ignore-version")),
                "shell": Flag(flag("--shell"))
            }
        )
        self.cli = ["mkdocs"] + extra_args + \
            self.schema.process(parameters)

    def build(
        self, clean: bool = None, dirty: bool = None, config_file: str = None,
        strict: bool = None, theme: Theme = None, use_directory_urls: bool = None,
        no_directory_urls: bool = None, site_dir: str = None, extra_args: list = []
    ) -> pipe:
        self.cli += ["build"] + extra_args + self.schema.process(locals())
        return self

    def gh_deploy(
        self, clean: bool = None, dirty: bool = None, message: str = None,
        remote_branch: str = None, remote_name: str = None, force: bool = None,
        no_history: bool = None, ignore_version: bool = None, shell: bool = None,
        config_file: str = None, strict: bool = None, theme: Theme = None,
        use_directory_urls: bool = None, no_directory_urls: bool = None,
        site_dir: str = None, extra_args: list = []
    ) -> pipe:
        self.cli += ["gh-deploy"] + extra_args + self.schema.process(locals())
        return self

    def new(self, target: str = None, extra_args: list = []) -> pipe:
        self.cli += ["new"] + extra_args + self.schema.process(locals())
        return self
