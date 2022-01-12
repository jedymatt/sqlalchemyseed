from dataclasses import dataclass

from sqlalchemy import ForeignKey, inspect, orm
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty

from sqlalchemyseed import errors


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
    value: object


# @dataclass
# class AttributeWrapper:
#     """
#     AttributeWrapper class is an InstrumentedAttribute wrapper
#     """

#     attribute: InstrumentedAttribute
#     """
#     An InstrumentedAttribute
#     """

#     is_column: bool
#     """
#     True if the attribute is a column

#     Ex.:
#         class SomeClass:
#             ...

#             value = Column(...)
#     """

#     is_relationship: bool
#     """
#     True if the attribute is a relationship

#      Ex.:
#         class SomeClass:
#             ...

#             value = relationship(...)
#     """

#     @classmethod
#     def from_attribute(cls, attr: object):
#         """
#         From attribute
#         """
#         insp: InstrumentedAttribute = inspect(attr, raiseerr=False)

#         if insp is None or not insp.is_attribute:
#             raise errors.InvalidTypeError("Invalid class attribute")

#         attribute: InstrumentedAttribute = insp
#         is_column = isinstance(insp.property, ColumnProperty)
#         is_relationship = isinstance(insp.property, RelationshipProperty)

#         return cls(attribute=attribute, is_column=is_column, is_relationship=is_relationship)

#     @classmethod
#     def from_instance(cls, instance: object, attribute_name: str):
#         """
#         From instance
#         """
#         attr = getattr(instance.__class__, attribute_name)
#         return cls.from_attribute(attr)

#     @property
#     def parent(self) -> orm.Mapper:
#         """
#         Parent of the attribute which is a class mapper
#         """
#         return self.attribute.parent

class AttributeWrapper:
    """
    AttributeWrapper class. A wrapper for InstrumentAttribute.
    """
    attr: InstrumentedAttribute
    """
    An InstrumentAttribute.
    To get an InstrumentedAttribute use `inspect(Class.attribute, raiseerr=False)`
    """
    is_column: bool
    """
    True if the attribute is a column

    Ex.:
        class SomeClass:
            ...

            value = Column(...)
    """

    is_relationship: bool
    """
    True if the attribute is a relationship

     Ex.:
        class SomeClass:
            ...

            value = relationship(...)
    """

    def __init__(self, class_attribute) -> None:
        class_attribute = inspect(class_attribute, raiseerr=False)

        if class_attribute is None or not class_attribute.is_attribute:
            raise errors.InvalidTypeError("Invalid class attribute")

        self.attr: InstrumentedAttribute = class_attribute
        self.is_column = isinstance(class_attribute.property, ColumnProperty)
        self.is_relationship = isinstance(
            class_attribute.property,
            RelationshipProperty
        )
        self._cache_ref_class = None

    @property
    def parent(self) -> orm.Mapper:
        """
        Parent of the attribute which is a class mapper.
        """

        return self.attr.parent

    @property
    def class_(self) -> object:
        """
        Returns a parent class.
        """
        return self.attr.parent.class_

    @property
    def prop(self):
        """
        MapperProperty
        """
        return self.attr.property

    @property
    def referenced_class(self):
        """
        Referenced class.
        Returns None if there is no referenced class
        """
        if self._cache_ref_class is not None:
            return self._cache_ref_class

        if self.is_relationship:
            self._cache_ref_class = self.attr.mapper.class_
            return self._cache_ref_class

        if self.is_column:
            foreign_key: ForeignKey = next(iter(self.attr.foreign_keys), None)
            if foreign_key is None:
                return None

            self._cache_ref_class = next(filter(
                lambda mapper: mapper.tables[0].name == foreign_key.column.table.name,
                self.attr.parent.registry.mappers
            )).class_

        return self._cache_ref_class


class AttributeValue(AttributeWrapper):
    """
    Value container for AttributeWrapper
    """

    def __init__(self, attr, value) -> None:
        super().__init__(attr)
        self.value = value
