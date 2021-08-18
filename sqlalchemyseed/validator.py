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


class Key:
    def __init__(self, label: str, type_):
        self.label = label
        self.type = type_

    def unpack(self):
        return self.label, self.type

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

    @classmethod
    def source_keys(cls):
        """The possible pairs of model key [data, filter]

        Returns:
            list: list of keys object
        """
        return [cls.data(), cls.filter()]

    @classmethod
    def source_keys_labels(cls) -> list:
        return [source_key.label for source_key in cls.source_keys()]

    def __repr__(self):
        return "<{}(label='{}', type='{}')>".format(self.__class__.__name__, self.label, self.type)


def validate_key(key: Key, entity: dict):
    if key.label not in entity:
        raise KeyError("Key {} not found".format(key.label))
    if not isinstance(entity[key.label], key.type):
        raise TypeError("Invalid type, entity['{}'] type is not '{}'".format(key.label, key.type))


class SchemaValidator:
    __model_key = Key.model()
    __source_keys = Key.source_keys()

    @classmethod
    def validate(cls, entities, ref_prefix='!'):
        cls._pre_validate(entities, is_parent=True, ref_prefix=ref_prefix)

    @classmethod
    def _pre_validate(cls, entities: dict, is_parent=True, ref_prefix='!'):
        if isinstance(entities, dict):
            if len(entities) == 0:
                return
            cls._validate(entities, is_parent, ref_prefix)
        elif isinstance(entities, list):
            for item in entities:
                cls._pre_validate(item, is_parent, ref_prefix)
        else:
            raise TypeError("Invalid type, should be list or dict")

    @classmethod
    def _validate(cls, entity: dict, is_parent=True, ref_prefix='!'):
        if len(entity) > 2:
            raise ValueError("Should not have items for than 2.")

        try:
            validate_key(cls.__model_key, entity)
        except KeyError as error:
            if is_parent:
                raise error

        # get source key, either data or filter key
        source_key = next(
            (sk for sk in cls.__source_keys if sk.label in entity.keys()),
            None)

        # check if current keys has at least, data or filter key
        if source_key is None:
            raise KeyError("Missing 'data' or 'filter' key.")

        source_data = entity[source_key.label]

        if isinstance(source_data, list):
            if len(source_data) == 0:
                raise ValueError(f"'{source_key.label}' is empty.")

            for item in source_data:
                if not source_key.is_valid_type(item):
                    raise TypeError(
                        f"Invalid type, '{source_key.label}' should be '{source_key.type}'")

                # check if item is a relationship attribute
                cls._scan_attributes(item, ref_prefix)
        elif source_key.is_valid_type(source_data):
            # check if item is a relationship attribute
            cls._scan_attributes(source_data, ref_prefix)
        else:
            raise TypeError(
                f"Invalid type, '{source_key.label}' should be '{source_key.type}'")

    @classmethod
    def _scan_attributes(cls, source_data: dict, ref_prefix):
        for key, value in source_data.items():
            if str(key).startswith(ref_prefix):
                cls._pre_validate(value, is_parent=False, ref_prefix=ref_prefix)


if __name__ == '__main__':
    pass
