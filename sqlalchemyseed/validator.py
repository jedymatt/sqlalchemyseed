"""
MIT License

Copyright (c) 2021 Jedy Matt Tabasco

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from . import errors


class Key:
    def __init__(self, label: str, type_):
        self.label = label
        self.type = type_

    # def unpack(self):
    #     return self.label, self.type

    @classmethod
    def model(cls):
        return cls('model', str)

    @classmethod
    def data(cls):
        return cls('data', dict)

    @classmethod
    def filter(cls):
        return cls('filter', dict)

    def is_valid_type(self, entity):
        return isinstance(entity, self.type)

    def __str__(self):
        return self.label

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.label == o.label and self.type == o.type

        if isinstance(o, str):
            return self.label == o

        return False

    def __hash__(self):
        return hash(self.label)


def check_model_key(entity: dict, entity_is_parent: bool):
    model = Key.model()
    if model not in entity and entity_is_parent:
        raise errors.MissingRequiredKeyError("'model' key is missing.")
    # check type
    if model in entity and not model.is_valid_type(entity[model]):
        raise errors.InvalidDataTypeError("'model' data should be 'string'.")


def check_max_length(entity: dict):
    if len(entity) > 2:
        raise errors.MaxLengthExceededError("Length should not exceed by 2.")


def check_source_key(entity: dict, source_keys: list) -> Key:
    source_key: Key = next(
        (sk for sk in source_keys if sk in entity),
        None
    )

    # check if current keys has at least, data or filter key
    if source_key is None:
        raise errors.MissingRequiredKeyError("Missing 'data' or 'filter' key.")

    return source_key


def check_source_data(source_data, source_key: Key):
    if not isinstance(source_data, dict) and not isinstance(source_data, list):
        raise errors.InvalidDataTypeError(f"Invalid type, {str(source_key)} should be either 'dict' or 'list'.")

    if isinstance(source_data, list) and len(source_data) == 0:
        raise errors.EmptyDataError("Empty list, 'data' or 'filter' list should not be empty.")


# def iter_reference_relationships(kwargs: dict, ref_prefix):
#     for attr_name, value in kwargs.items():
#         if attr_name.startswith(ref_prefix):
#             # removed prefix
#             yield attr_name[len(ref_prefix):], value


class SchemaValidator:
    _source_keys = None

    @classmethod
    def validate(cls, entities, ref_prefix='!', source_keys=None):
        if source_keys is None:
            cls._source_keys = [Key.data(), Key.filter()]
        cls._pre_validate(entities, is_parent=True, ref_prefix=ref_prefix)

    @classmethod
    def _pre_validate(cls, entities: dict, is_parent=True, ref_prefix='!'):
        if not isinstance(entities, dict) and not isinstance(entities, list):
            raise errors.InvalidDataTypeError("Invalid type, should be list or dict")
        if len(entities) == 0:
            return
        if isinstance(entities, dict):
            return cls._validate(entities, is_parent, ref_prefix)
        # iterate list
        for entity in entities:
            cls._pre_validate(entity, is_parent, ref_prefix)

    @classmethod
    def _validate(cls, entity: dict, entity_is_parent=True, ref_prefix='!'):
        check_max_length(entity)
        check_model_key(entity, entity_is_parent)

        # get source key, either data or filter key
        source_key = check_source_key(entity, cls._source_keys)
        source_data = entity[source_key]

        check_source_data(source_data, source_key)

        if isinstance(source_data, list):
            for item in source_data:
                if not source_key.is_valid_type(item):
                    raise errors.InvalidDataTypeError(
                        f"Invalid type, '{source_key.label}' should be '{source_key.type}'")

                # check if item is a relationship attribute
                cls._scan_attributes(item, ref_prefix)
        elif source_key.is_valid_type(source_data):
            # check if item is a relationship attribute
            cls._scan_attributes(source_data, ref_prefix)

    @classmethod
    def _scan_attributes(cls, source_data: dict, ref_prefix):
        for key, value in source_data.items():
            if str(key).startswith(ref_prefix):
                cls._pre_validate(value, is_parent=False, ref_prefix=ref_prefix)
