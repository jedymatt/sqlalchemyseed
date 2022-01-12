from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.attributes import get_attribute
from sqlalchemy.orm.attributes import set_attribute
from sqlalchemy.orm.base import object_mapper
from inspect import isclass

from sqlalchemy.sql.operators import isnot


def get_instrumented_attribute(object_or_class, key: str):
    """
    Returns instrumented attribute from the object or class.
    """

    if isclass(object_or_class):
        return getattr(object_or_class, key)

    return getattr(object_or_class.__class__, key)


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


def foreign_key_column(instrumented_attr: InstrumentedAttribute):
    """
    Returns the table name of the first foreignkey.
    """
    return next(iter(instrumented_attr.foreign_keys)).column


def referenced_class(instrumented_attr: InstrumentedAttribute):
    """
    Returns class that the attribute is referenced to.
    """

    if attr_is_relationship(instrumented_attr):
        return instrumented_attr.mapper.class_

    table_name = foreign_key_column(instrumented_attr).table.name

    return next(filter(
        lambda mapper: mapper.class_.__tablename__ == table_name,
        # object_mapper(instance).registry.mappers
        instrumented_attr.parent.registry.mappers
    )).class_
