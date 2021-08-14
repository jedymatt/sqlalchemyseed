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

from typing import NamedTuple
from collections import namedtuple


try:
    from .class_cluster import ClassCluster
except ImportError:
    from class_cluster import ClassCluster


def __path_str(path: list):
    return '.'.join(path)


class __Tree:
    def __init__(self, obj=None):
        self.obj = obj

        self._current_path = []

    def walk(self, obj=None):
        if obj is None:
            obj = self.obj
        self._walk(obj)

    def _walk(self, obj):
        # convert list into dict
        if isinstance(obj, list):
            obj = {str(key): value for key, value in enumerate(obj)}

        if isinstance(obj, dict):
            for key, value in obj.items():
                self._current_path.append(key)
                # print(f"\'{path_str(self.path)}\'", '=', value)

                if isinstance(value, list) or isinstance(value, dict):
                    # print(f"\'{path_str(self.path)}\'", '=', value)
                    self._walk(value)
                else:
                    # if leaf
                    # print(f"\'{self.current_path}\'", '=', value)
                    pass
                self._current_path.pop()
        else:
            return print(obj)


class SchemaValidator:
    # root_type = dict
    # root_length = 2
    __required_keys = (
        ('model', 'data'),
        ('model', 'filter')
    )
    __model_type = str
    __entity_types = [dict, list]

    @classmethod
    def validate(cls, obj):
        if isinstance(obj, list):
            for i in obj:
                cls.validate(i)
        else:
            cls._validate(obj)

    @classmethod
    def _validate(cls, obj):
        if not isinstance(obj, dict):
            raise TypeError('\'obj\' object is not type \'dict\'.')

        if len(obj) > 2:
            raise ValueError('obj length exceeds to \'2\'')
        # elif len(obj) < 2:
        #     raise ValueError('obj length lesser than \'2\'')
        elif len(obj) == 0:
            return

        obj_keys = None
        for keys in cls.__required_keys:
            if all(key in obj.keys() for key in keys):
                obj_keys = keys
                break

        if obj_keys is None:
            raise KeyError('keys not accepted')

        if not isinstance(obj[obj_keys[0]], cls.__model_type):
            raise TypeError(f'obj[{obj_keys[0]}] is not type \'str\'')
        if type(obj[obj_keys[1]]) not in cls.__entity_types:
            raise KeyError(
                f'obj[{obj_keys[1]}] is not type \'dict\' or \'list\'')
        # print(obj_keys[1], '=', obj[obj_keys[1]])
        if isinstance(obj[obj_keys[1]], list):
            if len(obj[obj_keys[1]]) == 0:
                raise ValueError(f'obj[{obj_keys[1]}]: value is empty')
            elif not all(isinstance(item, dict) for item in obj[obj_keys[1]]):
                raise TypeError(
                    f'\'obj[{obj_keys[1]}]\': items is not type \'dict\'')
            else:
                for items in obj[obj_keys[1]]:
                    for k, v in items.items():
                        if str(k).startswith('!'):
                            cls.validate(v)
        elif isinstance(obj[obj_keys[1]], dict):
            # print(obj_keys[1], '=', obj[obj_keys[1]])
            for k, v in obj[obj_keys[1]].items():
                # print(f'{k}, {v}')
                if str(k).startswith('!'):
                    cls.validate(v)


class FutureKey:
    def __init__(self, label: str, type_: list):
        self.label = label
        self.type = type_

    def unpack(self):
        return self.label, self.type

    @classmethod
    def model(cls):
        return cls('model', str)

    @classmethod
    def filter(cls):
        return cls('filter', dict)

    @classmethod
    def data(cls):
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

    # @classmethod
    # def iter_source_keys(cls):
    #     for source_key in cls.source_keys():
    #         yield source_key.unpack()

    @classmethod
    def source_keys_labels(cls) -> list:
        return [source_key.label for source_key in cls.source_keys()]

    def __repr__(self):
        return "<{}(label='{}', type='{}')>".format(self.__class__.__name__, self.label, self.type)


Parent = namedtuple('Parent', ['label', 'instance'])


class FutureSchemaValidator:
    _ccluster = ClassCluster()
    __model_key = FutureKey.model()
    __source_keys = FutureKey.source_keys()

    @classmethod
    def validate(cls, entities, prefix='!'):
        cls._ccluster.clear()

        cls._pre_validate(entities, prefix)

    @classmethod
    def _pre_validate(cls, entities, prefix, parent: Parent = None):
        if isinstance(entities, dict):
            cls._validate(entities, prefix, parent)
        elif isinstance(entities, list):
            for item in entities:
                cls._validate(item, prefix, parent)
        else:
            raise TypeError("invalid type, should be list or dict")

    @classmethod
    def _validate(cls, entity: dict, prefix, parent):
        if not isinstance(entity, dict):
            raise TypeError("invalid type, should be dict")

        if len(entity) > 2:
            raise ValueError("should not have items for than 2.")

        if len(entity) == 0:
            return

        if parent is None:
            model_key = cls.__model_key
            # check if the current keys has model key
            if model_key.label not in entity.keys():
                raise ValueError("Missing required 'model' key.")

            model_data = entity[model_key.label]
            # check if key model is valid
            if not model_key.is_valid_type(model_data):
                raise TypeError(
                    f"Invalid type, '{model_key.label}' should be '{model_key.type}'")

        # get source key, either data or filter key
        source_key = next(
            (sk for sk in cls.__source_keys if sk.label in entity.keys()),
            None)

        # check if current keys has at least, data or filter key
        if source_key is None:
            raise KeyError("Missing 'data' or 'filter' key.")

        source_data = entity[source_key.label]

        if isinstance(source_data, list):
            for item in source_data:
                if not source_key.is_valid_type(item):
                    raise TypeError(
                        f"Invalid type, '{source_key.label}' should be '{source_key.type}'")

                # check if item is a relationship attribute
        elif source_key.is_valid_type(source_data):
            # check if item is a relationship attribute
            return

        # else
        raise TypeError(
            f"Invalid type, '{source_key.label}' should be '{source_key.type}'")

    @classmethod
    def _check_children(cls, source_data: dict, prefix):
        for key, value in source_data.items():
            if str(key).startswith(prefix):
                # TODO: parent unfilled
                parent = Parent(label=str(key), )
                cls._pre_validate(value, prefix, parent=parent)

if __name__ == '__main__':
    FutureSchemaValidator.validate({
    })
    FutureSchemaValidator.validate({})
    pass
