"""
Utility functions
"""


from typing import Iterable

from sqlalchemy import inspect


def iter_ref_kwargs(kwargs: dict, ref_prefix: str):
    """
    Iterate kwargs with name prefix or references
    """
    for attr_name, value in kwargs.items():
        if attr_name.startswith(ref_prefix):
            # removed prefix
            yield attr_name[len(ref_prefix):], value


def iter_kwargs_with_prefix(kwargs: dict, prefix: str):
    """
    Iterate kwargs(dict) that has the specified prefix.
    """
    for key, value in kwargs.items():
        if str(key).startswith(prefix):
            yield key, value


def iterate_json(json: dict, key_prefix: str):
    """
    Iterate through json that has matching key prefix
    """
    for key, value in json.items():
        has_prefix = str(key).startswith(key_prefix)

        if has_prefix:
            # removed prefix
            yield key[len(key_prefix):], value


def iterate_json_no_prefix(json: dict, key_prefix: str):
    """
    Iterate through json that has no matching key prefix
    """
    for key, value in json.items():
        has_prefix = str(key).startswith(key_prefix)
        if not has_prefix:
            yield key, value


def iter_non_ref_kwargs(kwargs: dict, ref_prefix: str):
    """Iterate kwargs, skipping item with name prefix or references"""
    for attr_name, value in kwargs.items():
        if not attr_name.startswith(ref_prefix):
            yield attr_name, value


def is_supported_class(class_):
    """
    Check if it is a class and supports sqlalchemy
    """
    insp = inspect(class_, raiseerr=False)
    # insp.is_mapper means it is a mapped class
    return insp is not None and insp.is_mapper


def generate_repr(instance: object) -> str:
    """
    Generate repr of object instance
    """
    class_name = instance.__class__.__name__
    insp = inspect(instance)
    attributes = {column.key: column.value for column in insp.attrs}
    str_attributes = ",".join(f"{k}='{v}'" for k, v in attributes.items())
    return f"<{class_name}({str_attributes})>"


def find_item(json: Iterable, keys: list):
    """
    Finds item of json from keys
    """
    return find_item(json[keys[0]], keys[1:]) if keys else json
