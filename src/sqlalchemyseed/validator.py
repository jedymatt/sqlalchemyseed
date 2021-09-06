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

from . import errors, util


class Key:
    def __init__(self, name: str, type_):
        self.name = name
        self.type_ = type_

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
        return isinstance(entity, self.type_)

    def __str__(self):
        return self.name

    def __eq__(self, o: object) -> bool:
        if isinstance(o, self.__class__):
            return self.name == o.name and self.type_ == o.type_

        if isinstance(o, str):
            return self.name == o

        return False

    def __hash__(self):
        return hash(self.name)


def check_model_key(entity: dict, entity_is_parent: bool):
    model = Key.model()
    if model not in entity and entity_is_parent:
        raise errors.MissingKeyError("'model' key is missing.")
    # check type_
    if model in entity and not model.is_valid_type(entity[model]):
        raise errors.InvalidTypeError("'model' data should be 'string'.")


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
        raise errors.MissingKeyError(
            f"Missing {', '.join(map(str, source_keys))} key(s).")

    return source_key


def check_source_data(source_data, source_key: Key):
    if not isinstance(source_data, dict) and not isinstance(source_data, list):
        raise errors.InvalidTypeError(
            f"Invalid type_, {str(source_key)} should be either 'dict' or 'list'.")

    if isinstance(source_data, list) and len(source_data) == 0:
        raise errors.EmptyDataError(
            "Empty list, 'data' or 'filter' list should not be empty.")


def check_data_type(item, source_key: Key):
    if not source_key.is_valid_type(item):
        raise errors.InvalidTypeError(
            f"Invalid type_, '{source_key.name}' should be '{source_key.type_}'")


class SchemaValidator:

    def __init__(self, source_keys, ref_prefix):
        self._source_keys = source_keys
        self._ref_prefix = ref_prefix

    def validate(self, entities):
        self._pre_validate(entities, entity_is_parent=True)

    def _pre_validate(self, entities: dict, entity_is_parent=True):
        if not isinstance(entities, dict) and not isinstance(entities, list):
            raise errors.InvalidTypeError(
                "Invalid type, should be list or dict")
        if len(entities) == 0:
            return
        if isinstance(entities, dict):
            return self._validate(entities, entity_is_parent)
        # iterate list
        for entity in entities:
            self._pre_validate(entity, entity_is_parent)

    def _validate(self, entity: dict, entity_is_parent=True):
        check_max_length(entity)
        check_model_key(entity, entity_is_parent)

        # get source key, either data or filter key
        source_key = check_source_key(entity, self._source_keys)
        source_data = entity[source_key]

        check_source_data(source_data, source_key)

        if isinstance(source_data, list):
            for item in source_data:
                check_data_type(item, source_key)
                # check if item is a relationship attribute
                self.check_attributes(item)
        else:
            # source_data is dict
            # check if item is a relationship attribute
            self.check_attributes(source_data)

    def check_attributes(self, source_data: dict):
        for _, value in util.iter_ref_kwargs(source_data, self._ref_prefix):
            self._pre_validate(value, entity_is_parent=False)


def validate(entities, ref_prefix='!'):

    SchemaValidator(source_keys=[Key.data()], ref_prefix=ref_prefix) \
        .validate(entities=entities)


def hybrid_validate(entities, ref_prefix='!'):

    SchemaValidator(source_keys=[Key.data(), Key.filter()], ref_prefix=ref_prefix) \
        .validate(entities=entities)
