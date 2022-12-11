class Argument:
    def __init__(self, val) -> None:
        self.val = val


class Flag(Argument):
    pass


class Once(Argument):
    pass


class Repeat(Argument):
    pass


class List(Argument):
    pass


class Schema(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(*args, **kwargs)

    def __setitem__(self, key: str, value: Argument):
        dict.__setitem__(key, value)

    def parse_arguments(self) -> list:
        pass

def parse(
    variables: dict, args: dict, reflection: dict[str, Argument]
) -> list:
    for k, v in variables.items():
        if v is not None:
            arg = reflection.get(k)
            val = getattr(v, "value", v)
            if arg is not None:
                args[arg.val] = val

    processed_args = []
    for k, v in args.items():
        if type(v) == list:
            for o in v:
                val = getattr(o, "value", o)
                processed_args.extend([k, val])
        else:
            processed_args.extend([k, v])

    return processed_args
