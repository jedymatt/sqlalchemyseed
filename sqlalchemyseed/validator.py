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


class SchemaValidator:
    __model_key = Key.model()
    __source_keys = Key.source_keys()

    @classmethod
    def validate(cls, entities, ref_prefix='!'):
        cls._pre_validate(entities, is_parent=True, ref_prefix=ref_prefix)

    @classmethod
    def _pre_validate(cls, entities, is_parent=True, ref_prefix='!'):
        if isinstance(entities, dict):
            cls._validate(entities, is_parent, ref_prefix)
        elif isinstance(entities, list):
            for item in entities:
                cls._validate(item, is_parent, ref_prefix)
        else:
            raise TypeError("Invalid type, should be list or dict")

    @classmethod
    def _validate(cls, entity: dict, is_parent=True, ref_prefix='!'):
        if not isinstance(entity, dict):
            raise TypeError("Invalid type, should be dict")

        if len(entity) > 2:
            raise ValueError("Should not have items for than 2.")
        elif len(entity) == 0:
            return

        # check if the current keys has model key
        if cls.__model_key.label not in entity.keys():
            if is_parent:
                raise KeyError(
                    "Missing 'model' key. 'model' key is required when entity is not a parent.")
        else:
            model_data = entity[cls.__model_key.label]
            # check if key model is valid
            if not cls.__model_key.is_valid_type(model_data):
                raise TypeError(
                    f"Invalid type, '{cls.__model_key.label}' should be '{cls.__model_key.type}'")

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
