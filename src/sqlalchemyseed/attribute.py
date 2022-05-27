"""
attribute module containing helper functions for instrumented attribute.
"""

from functools import lru_cache
from inspect import isclass

from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute, get_attribute, set_attribute


def instrumented_attribute(class_or_instance, key: str):
    """
    Returns instrumented attribute from the class or instance.
    """

    if isclass(class_or_instance):
        return getattr(class_or_instance, key)

    return getattr(class_or_instance.__class__, key)


def attr_is_relationship(instrumented_attr: InstrumentedAttribute):
    """
    Check if instrumented attribute property is a RelationshipProperty
    """
    return isinstance(instrumented_attr.property, RelationshipProperty)


def attr_is_column(instrumented_attr: InstrumentedAttribute):
    """
    Check if instrumented attribute property is a ColumnProperty
    """
    return isinstance(instrumented_attr.property, ColumnProperty)


def set_instance_attribute(instance, key, value):
    """
    Set attribute value of instance
    """

    instr_attr: InstrumentedAttribute = getattr(instance.__class__, key)

    if attr_is_relationship(instr_attr) and instr_attr.property.uselist:
        get_attribute(instance, key).append(value)
    else:
        set_attribute(instance, key, value)

@lru_cache()
def foreign_key_column(instrumented_attr: InstrumentedAttribute):
    """
    Returns the table name of the first foreignkey.
    """
    return next(iter(instrumented_attr.foreign_keys)).column

@lru_cache()
def referenced_class(instrumented_attr: InstrumentedAttribute):
    """
    Returns class that the attribute is referenced to.
    """

    if attr_is_relationship(instrumented_attr):
        return instrumented_attr.mapper.class_

    table_name = foreign_key_column(instrumented_attr).table.name

    return next(filter(
        lambda mapper: mapper.class_.__tablename__ == table_name,
        instrumented_attr.parent.registry.mappers
    )).class_
