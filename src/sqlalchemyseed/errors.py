class ClassNotFoundError(Exception):
    """Raised when the class is not found"""


class MissingKeyError(Exception):
    """Raised when a required key is missing"""


class MaxLengthExceededError(Exception):
    """Raised when maximum length of data exceeded"""


class InvalidTypeError(Exception):
    """Raised when a type of data is not accepted"""


class EmptyDataError(Exception):
    """Raised when data is empty"""


class InvalidKeyError(Exception):
    """Raised when an invalid key is invoked"""


class ParseError(Exception):
    """Raised when parsing string fails"""


class UnsupportedClassError(Exception):
    """Raised when an unsupported class is invoked"""


class NotInModuleError(Exception):
    """Raised when a value is not found in module"""


class InvalidModelPath(Exception):
    """Raised when an invalid model path is invoked"""
