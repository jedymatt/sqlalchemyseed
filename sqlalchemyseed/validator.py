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


class KeyValidator:
    __keys = {'model': [str], 'data': [list, dict], 'filter': [list, dict]}

    @classmethod
    def is_valid(cls, key: str, obj):
        if key not in cls.__keys.keys():
            raise KeyError('Invalid Key')
        
        key_types = cls.__keys[key]

        for key_type in key_types:
            if isinstance(obj, key_type):
                return True

        return False

    @classmethod
    def is_valid_model(cls,  obj):
        return cls.is_valid('model', obj)

    @classmethod
    def is_valid_data(cls,  obj):
        return cls.is_valid('data', obj)

    @classmethod
    def is_valid_filter(cls,  obj):
        return cls.is_valid('filter', obj)


class FutureSchemaValidator:
    _ccluster = ClassCluster()
    __parent_keys = [('model', str), ('data', list, dict),
                     ('filter', list, dict)]

    @classmethod
    def validate(cls, entities, prefix='!'):
        cls._ccluster.clear()


if __name__ == '__main__':
    FutureSchemaValidator.__model_type = int
    FutureSchemaValidator.validate({})
    # print(KeyValidator.is_valid_model(''))
    # print(KeyType().model)
