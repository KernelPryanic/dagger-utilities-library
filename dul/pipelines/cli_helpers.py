class Argument:
    def __init__(
        self, format: callable
    ) -> None:
        self.format = format


class Flag(Argument):
    pass


class Positional(Argument):
    pass


class Once(Argument):
    pass


class Repeat(Argument):
    pass


class Schema(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(*args, **kwargs)

    def __setitem__(self, key: str, value: Argument):
        dict.__setitem__(key, value)

    def __getitem__(self, key: str) -> Argument:
        return dict.__getitem__(key)

    def process(self, variables: dict) -> list:
        args = []
        for var_name, var_value in variables.items():
            if var_value is not None:
                arg: Argument = self.get(var_name)
                arg_val = getattr(var_value, "value", var_value)
                match type(arg):
                    case Flag():
                        args.append(arg.format())
                    case Positional():
                        v = getattr(arg_val, "value", arg_val)
                        args.append(arg.format(v))
                    case Once():
                        v = getattr(arg_val, "value", arg_val)
                        args.extend(arg.format(v))
                    case Repeat():
                        match type(arg_val):
                            case list():
                                for item in arg_val:
                                    v = getattr(item, "value", item)
                                    args.extend(arg.format(v))
                            case dict():
                                for k, v in arg_val.items():
                                    v = getattr(item, "value", item)
                                    args.extend(arg.format(k, v))
                    case None:
                        pass

        return args