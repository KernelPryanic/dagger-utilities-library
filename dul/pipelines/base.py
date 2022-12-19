from dagger.api.gen import Container

from ..common.structlogging import *
from .generic import get_job_name

log = structlog.get_logger()


class Argument:
    def __init__(
        self, format: callable
    ) -> None:
        self.format = format


class Flag(Argument):
    ...


class Positional(Argument):
    ...


class Once(Argument):
    ...


class Repeat(Argument):
    ...


class Schema(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key: str, value: Argument):
        dict.__setitem__(self, key, value)

    def __getitem__(self, key: str) -> Argument:
        return dict.__getitem__(self, key)

    def process(self, variables: dict) -> list:
        args = []
        for var_name, arg in self.items():
            var_value = variables.get(var_name)
            if var_value is not None:
                arg_val = getattr(var_value, "value", var_value)
                match arg:
                    case Flag():
                        args.extend(arg.format())
                    case Positional():
                        v = getattr(arg_val, "value", arg_val)
                        args.extend(arg.format(v))
                    case Once():
                        v = getattr(arg_val, "value", arg_val)
                        args.extend(arg.format(v))
                    case Repeat():
                        match arg_val:
                            case list():
                                for item in arg_val:
                                    v = getattr(item, "value", item)
                                    args.extend(arg.format(v))
                            case dict():
                                for k, v in arg_val.items():
                                    v = getattr(v, "value", v)
                                    args.extend(arg.format(k, v))
                    case None:
                        pass

        return args


class pipe():
    def __init__(self):
        self.schema: dict
        self.cli: list
        self.parent: pipe

    def __call__(
        self, container: Container, root: str = None,
    ) -> Container:
        pipeline = container
        if root is not None:
            pipeline = container.with_workdir(root)

        log.info("Executing", job=get_job_name(), command=self.cli)

        return (
            pipeline.
            with_exec(self.cli)
        )
