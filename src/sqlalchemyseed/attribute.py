"""
attribute module containing helper functions for instrumented attribute.
"""

import warnings
from functools import lru_cache
from inspect import isclass

from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute, get_attribute, set_attribute

from . import errors


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


def check_scalar_cardinality(instance, attr_name, value, strict=False):
    """
    Guard against binding a list to a scalar relationship (gap #4).

    A scalar relationship (``uselist=False``) given a list keeps only the last
    element via repeated assignment — silent data loss. When ``value`` is a
    list of more than one item, this raises if ``strict`` else warns. A
    single-element list is left alone (assigning one element is correct).

    This guard only inspects the child ``value`` itself: it does not detect
    the equivalent last-wins case expressed as a nested ``data`` list (e.g.
    ``{"!company": {"data": [{...}, {...}]}}``), which remains out of scope
    for gap #4.
    """
    instr_attr = instrumented_attribute(instance, attr_name)
    if not attr_is_relationship(instr_attr):
        return
    if instr_attr.property.uselist:
        return
    if not isinstance(value, list) or len(value) <= 1:
        return
    message = (
        f"relationship {attr_name!r} is scalar (uselist=False) but received "
        f"a list of {len(value)} items"
    )
    if strict:
        raise errors.InvalidTypeError(message)
    warnings.warn(message, stacklevel=2)


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
