"""Common exceptions for DUL."""


class DULException(Exception):
    """Base exception for all DUL exceptions"""


class MissingEnvVar(DULException):
    """Exception for missing environment variables"""

    def __init__(self, name):
        DULException.__init__(self, f"Environment variable is not set: {name}")
