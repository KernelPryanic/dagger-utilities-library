from enum import Enum

from dagger.api.gen import Container

from .cli_helpers import Flag, Once, Positional, Schema, pipe
from .curl import curl


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


def list(name):
    return lambda values: [name, *[getattr(v, "value", v) for v in values]]


class cli(pipe):
    def __init__(
        self, config: str = None, footer_from: str = None, header_from: str = None,
        hide: list[Section] = None, lockfile: bool = None, output_check: bool = None,
        output_file: str = None, output_mode: OutputMode = None, output_template: str = None,
        output_values: bool = None, output_values_from: str = None, read_comments: bool = None,
        recursive: bool = None, recursive_path: str = None, show: list[Section] = None,
        sort_by: SortCriteria = None, version: bool = None, target: str = None, extra_args: list = []
    ) -> pipe:
        parameters = locals()
        self.schema = Schema(
            {
                "target": Positional(lambda v: [v]),
                "config": Once(once("--config")),
                "footer_from": Once(once("--footer-from")),
                "header_from": Once(once("--header-from")),
                "hide": Once(list("--hide")),
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
                "show": Once(list("--show")),
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

    def asciidoc(self, extra_args: list = []) -> __asciidoc:
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

    def markdown(self) -> __markdown:
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
            parameters = locals()
            self.cli = parent.cli + ["tfvars"] + \
                extra_args + self.schema.process(parameters)

        def hcl(self, extra_args: list = []) -> pipe:
            self.cli += ["hcl"] + extra_args
            return self

        def json(self, extra_args: list = []) -> pipe:
            self.cli += ["json"] + extra_args
            return self

    def toml(self, extra_args: list = []) -> pipe:
        self.cli += ["toml"] + extra_args
        return self

    def xml(self, extra_args: list = []) -> pipe:
        self.cli += ["xml"] + extra_args
        return self

    def yaml(self, extra_args: list = []) -> pipe:
        self.cli += ["xml"] + extra_args
        return self


class updater(pipe):
    def __init__(self, check: bool = None, target: str = None, extra_args: list = []):
        parameters = locals()
        self.schema = Schema(
            {
                "target": Positional(lambda v: [v]),
                "check": Flag(flag("-c"))
            }
        )
        self.cli = ["python", "-m", "dul.scripts.terraform.update_docs"] + extra_args + \
            self.schema.process(parameters)


def install(container: Container, version: str, root: str = None) -> Container:
    return (
        curl(
            redirect=True, silent=True, show_error=True, output="terraform-docs.tar.gz"
        ).get(
            f"https://terraform-docs.io/dl/v{version}/terraform-docs-v{version}-linux-amd64.tar.gz",
        )(container, root).
        with_exec(["tar", "-xzf", "terraform-docs.tar.gz"]).
        with_exec(["chmod", "+x", "terraform-docs"]).
        with_exec(["mv", "terraform-docs", "/usr/bin/"])
    )
