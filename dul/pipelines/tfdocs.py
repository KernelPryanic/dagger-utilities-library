from enum import Enum

from dagger.api.gen import Container

from . import curl
from .base import Flag, Once, Positional, Schema, pipe


class Section(Enum):
    ALL = "all"
    DATA_SOURCES = "data-sources"
    FOOTER = "footer"
    HEADER = "header"
    INPUTS = "inputs"
    MODULES = "modules"
    OUTPUTS = "outputs"
    PROVIDERS = "providers"
    REQUIREMENTS = "requirements"
    RESOURCES = "resources"


class OutputMode(Enum):
    INJECT = "inject"
    REPLACE = "replace"


class SortCriteria(Enum):
    NAME = "name"
    REQUIRED = "required"
    TYPE = "type"


def flag(name): return lambda: [name]
def once(name): return lambda value: [name, value]


def once_list(name):
    return lambda values: [name, *[getattr(v, "value", v) for v in values]]


class cli(pipe):
    def __init__(
        self, config: str = None, footer_from: str = None, header_from: str = None,
        hide: list[Section] = None, lockfile: bool = None, output_check: bool = None,
        output_file: str = None, output_mode: OutputMode = None, output_template: str = None,
        output_values: bool = None, output_values_from: str = None, read_comments: bool = None,
        recursive: bool = None, recursive_path: str = None, show: list[Section] = None,
        sort_by: SortCriteria = None, version: bool = None, path: str = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "path": Positional(lambda v: [v]),
                "config": Once(once("--config")),
                "footer_from": Once(once("--footer-from")),
                "header_from": Once(once("--header-from")),
                "hide": Once(once_list("--hide")),
                "lockfile": Flag(flag("--lockfile")),
                "output_check": Flag(flag("--output-check")),
                "output_file": Once(once("--output-file")),
                "output_mode": Once(once("--output-mode")),
                "output_template": Once(once("--output-template")),
                "output_values": Flag(flag("--output-values")),
                "output_values_from": Once(once("--output-values-from")),
                "read_comments": Flag(flag("--read-comments")),
                "recursive": Flag(flag("--recursive")),
                "recursive_path": Once(once("--recursive-path")),
                "show": Once(once_list("--show")),
                "sort": Flag(flag("--sort")),
                "sort_by": Once(once("--sort-by")),
                "version": Flag(flag("--version")),
                "escape": Flag(flag("--escape")),
                "color": Flag(flag("--color"))
            }
        )
        self.cli = ["terraform-docs"] + extra_args + \
            self.schema.process(parameters)

    class __asciidoc(pipe):
        def __init__(
            self, parent: pipe, anchor: bool = None, default: bool = None,
            hide_empty: bool = None, indent: int = None, required: bool = None,
            sensitive: bool = None, type: bool = None, extra_args: list = []
        ) -> pipe:
            parameters = locals()
            self.schema = Schema(
                {
                    "anchor": Flag(flag("--anchor")),
                    "default": Flag(flag("--default")),
                    "hide_empty": Flag(flag("--hide-empty")),
                    "indent": Once(once("--indent")),
                    "required": Flag(flag("--required")),
                    "sensitive": Flag(flag("--sensitive")),
                    "type": Flag(flag("--type"))
                }
            )
            self.cli = parent.cli + ["asciidoc"] + \
                extra_args + self.schema.process(parameters)

        def document(self, extra_args: list = []) -> pipe:
            self.cli += ["document"] + extra_args
            return self

        def table(self, extra_args: list = []) -> pipe:
            self.cli += ["table"] + extra_args
            return self

    def asciidoc(
        self, anchor: bool = None, default: bool = None,
        hide_empty: bool = None, indent: int = None, required: bool = None,
        sensitive: bool = None, type: bool = None, extra_args: list = []
    ) -> __asciidoc:
        return self.__asciidoc(self, locals())

    def json(self, escape: bool = None, extra_args: list = []) -> pipe:
        self.cli += ["json"] + extra_args + self.schema.process(locals())
        return self

    class __markdown(pipe):
        def __init__(
            self, parent: pipe, anchor: bool = None, default: bool = None,
            escape: bool = None, hide_empty: bool = None, html: bool = None,
            indent: int = None, required: bool = None, sensitive: bool = None,
            type: bool = None, extra_args: list = []
        ) -> pipe:
            parameters = locals()
            self.schema = Schema(
                {
                    "anchor": Flag(flag("--anchor")),
                    "default": Flag(flag("--default")),
                    "escape": Flag(flag("--escape")),
                    "hide_empty": Flag(flag("--hide-empty")),
                    "html": Flag(flag("--html")),
                    "indent": Once(once("--indent")),
                    "required": Flag(flag("--required")),
                    "sensitive": Flag(flag("--sensitive")),
                    "type": Flag(flag("--type"))
                }
            )
            self.cli = parent.cli + ["markdown"] + \
                extra_args + self.schema.process(parameters)

        def document(self, extra_args: list = []) -> pipe:
            self.cli += ["document"] + extra_args
            return self

        def table(self, extra_args: list = []) -> pipe:
            self.cli += ["table"] + extra_args
            return self

    def markdown(
        self,  anchor: bool = None, default: bool = None,
        escape: bool = None, hide_empty: bool = None, html: bool = None,
        indent: int = None, required: bool = None, sensitive: bool = None,
        type: bool = None, extra_args: list = []
    ) -> __markdown:
        return self.__markdown(self, locals())

    def pretty(self, color: bool = None, extra_args: list = []) -> pipe:
        self.cli += ["pretty"] + extra_args + self.schema.process(locals())
        return self

    class __tfvars(pipe):
        def __init__(
            self, parent: pipe, anchor: bool = None, default: bool = None,
            escape: bool = None, hide_empty: bool = None, html: bool = None,
            indent: int = None, required: bool = None, sensitive: bool = None,
            type: bool = None, extra_args: list = []
        ) -> pipe:
            self.cli = parent.cli + ["tfvars"] + \
                extra_args + self.schema.process(locals())

        def hcl(self, extra_args: list = []) -> pipe:
            self.cli += ["hcl"] + extra_args
            return self

        def json(self, extra_args: list = []) -> pipe:
            self.cli += ["json"] + extra_args
            return self

    def tfvars(
        self, anchor: bool = None, default: bool = None,
        escape: bool = None, hide_empty: bool = None, html: bool = None,
        indent: int = None, required: bool = None, sensitive: bool = None,
        type: bool = None, extra_args: list = []
    ) -> __tfvars:
        return self.__tfvars(self, locals())

    def toml(self, extra_args: list = []) -> pipe:
        self.cli += ["toml"] + extra_args
        return self

    def xml(self, extra_args: list = []) -> pipe:
        self.cli += ["xml"] + extra_args
        return self

    def yaml(self, extra_args: list = []) -> pipe:
        self.cli += ["yaml"] + extra_args
        return self


class scripts(pipe):
    def __init__(self) -> pipe:
        self.schema = Schema(
            {
                "dir": Positional(lambda v: [v]),
                "check": Flag(flag("--check"))
            }
        )

    def update(
        self, check: bool = None, directory: str = None, command: pipe = None, extra_args: list = []
    ) -> pipe:
        self.cli = (
            ["python", "-m", "dul.scripts.tfdoc.update"] +
            extra_args + ["--command", " ".join(command.cli + [directory])] +
            self.schema.process(locals())
        )
        return self


def install(container: Container, version: str, root: str = None) -> Container:
    binary_name = "terraform-docs"
    return (
        curl.cli(redirect=True, silent=True, show_error=True, output=f"{binary_name}.tar.gz").
        get(f"https://{binary_name}.io/dl/v{version}/{binary_name}-v{version}-linux-amd64.tar.gz")(container, root).
        with_exec(["tar", "-xzf", f"{binary_name}.tar.gz"]).
        with_exec(["chmod", "+x", f"{binary_name}"]).
        with_exec(["mv", f"{binary_name}", "/usr/local/bin/"])
    )
