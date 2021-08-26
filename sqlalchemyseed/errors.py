class ClassNotFoundError(Exception):
    """Raised when the class is not found"""
    pass


class MissingRequiredKeyError(Exception):
    """Raised when a required key is missing"""
    pass


class MaxLengthExceededError(Exception):
    """Raised when maximum length of data exceeded"""


class InvalidDataTypeError(Exception):
    """Raised when a type of data is not accepted"""


class EmptyDataError(Exception):
    """Raised when data is empty"""
