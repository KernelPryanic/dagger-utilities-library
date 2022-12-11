class Argument:
    def __init__(self, value) -> None:
        self.value = value


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

    def __getitem__(self, key: str) -> Argument:
        return dict.__getitem__(key)

    def process(self, variables: dict) -> list:
        args = []
        for var_name, var_value in variables.items():
            if var_value is not None:
                arg: Argument = self.get(var_name)
                arg_name = arg.value
                arg_val = getattr(var_value, "value", var_value)
                match type(arg):
                    case Flag():
                        args.append(arg_name)
                    case Once():
                        v = getattr(arg_val, "value", arg_val)
                        args.extend([arg_name, v])
                    case Repeat():
                        for item in arg_val:
                            v = getattr(item, "value", item)
                            args.extend([arg_name, v])
                    case List():
                        args.append(arg_name)
                        lst = "["
                        for item in arg_val:
                            v = getattr(item, "value", item)
                            lst += f"{v},"
                        lst = lst[:len(lst)-1] + "]"
                        args.append(lst)
                    case None:
                        pass

        return args
