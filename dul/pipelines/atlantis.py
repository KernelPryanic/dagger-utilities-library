from dul.pipelines.base import Flag, Once, Schema, pipe


def flag(name):
    return lambda: [name]


def once(name):
    return lambda value: [name, value]


class scripts(pipe):
    def __init__(self) -> pipe:
        self.schema = Schema(
            {"conf": Once(once("--conf")), "check": Flag(flag("--check"))}
        )

    def update_config(
        self, conf: str = None, check: bool = None, extra_args: list = []
    ) -> pipe:
        self.cli = (
            ["python", "-m", "dul.scripts.atlantis.update_config"]
            + self.schema.process(locals())
            + extra_args
        )
        return self
