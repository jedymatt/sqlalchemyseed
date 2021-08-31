class ClassNotFoundError(Exception):
    """Raised when the class is not found"""
    pass


class MissingKeyError(Exception):
    """Raised when a required key is missing"""
    pass


class MaxLengthExceededError(Exception):
    """Raised when maximum length of data exceeded"""
    pass


class InvalidTypeError(Exception):
    """Raised when a type of data is not accepted"""
    pass


class EmptyDataError(Exception):
    """Raised when data is empty"""
    pass


class InvalidKeyError(Exception):
    """Raised when an invalid key is invoked"""
    pass