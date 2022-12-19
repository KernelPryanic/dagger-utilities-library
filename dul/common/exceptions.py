class DULException(Exception):
    ...


class MissingEnvVar(DULException):
    def __init__(self, name):
        DULException.__init__(self, f"Environment variable is not set: {name}")
