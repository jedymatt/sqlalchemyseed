class ClassNotFoundError(Exception):
    """Raised when the class is not found"""


class MissingKeyError(Exception):
    """Raised when a required key is missing"""


class InvalidTypeError(Exception):
    """Raised when a type of data is not accepted"""


class EmptyDataError(Exception):
    """Raised when data is empty"""


class InvalidKeyError(Exception):
    """Raised when an invalid key is invoked"""


# Deprecated alias: sqlalchemyseed<=2.4.0 raised MaxLengthExceededError for
# entities with too many keys; those cases now raise InvalidKeyError. Kept so
# existing imports and except clauses keep working.
MaxLengthExceededError = InvalidKeyError


class ParseError(Exception):
    """Raised when parsing string fails"""


class UnsupportedClassError(Exception):
    """Raised when an unsupported class is invoked"""


class NotInModuleError(Exception):
    """Raised when a value is not found in module"""


class InvalidModelPath(Exception):
    """Raised when an invalid model path is invoked"""
