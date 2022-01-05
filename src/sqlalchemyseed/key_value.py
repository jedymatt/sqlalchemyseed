from dataclasses import dataclass

import sqlalchemy
from sqlalchemy import inspect, orm
from sqlalchemy.orm.attributes import InstrumentedAttribute, QueryableAttribute
from sqlalchemy.orm.state import AttributeState, InstanceState

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


@dataclass
class Attribute:
    """
    Attribute class
    """
    value: InstrumentedAttribute

    @property
    def property(self):
        """
        Attribute property
        """
        return self.value.property
        # return self.value.property
# key_value = KeyValue(key="key")

# print(key_value == KeyValue(key="key", value="fre"))
# print(str(key_value))
