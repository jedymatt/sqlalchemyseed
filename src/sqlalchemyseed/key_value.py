from dataclasses import dataclass

from sqlalchemy import inspect
from sqlalchemy.orm.state import InstanceState

from sqlalchemyseed.util import is_supported_class


def get_class(obj):
    """
    Get class of an object
    """
    return obj.__class__


@dataclass(frozen=True)
class KeyValue:
    """
    Key-value pair class
    """
    key: str
    value: object = None

# key_value = KeyValue(key="key")

# print(key_value == KeyValue(key="key", value="fre"))
# print(str(key_value))

