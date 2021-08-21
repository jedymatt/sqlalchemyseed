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

from collections import namedtuple
from typing import NamedTuple

import sqlalchemy.orm
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import object_mapper

try:  # relative import
    from . import validator
    from .class_registry import ClassRegistry, parse_class_path
    from . import errors
except ImportError:
    import validator
    from class_registry import ClassRegistry, parse_class_path
    import errors


# class Seeder:
#     def __init__(self, session: sqlalchemy.orm.Session = None):
#         self._session = session
#         self._class_registry = ClassRegistry()
#         self._instances = []

#         self._required_keys = [("model", "data")]

#     @property
#     def session(self):
#         return self._session

#     @session.setter
#     def session(self, value):
#         if not isinstance(value, sqlalchemy.orm.Session):
#             raise TypeError("obj type is not 'Session'.")

#         self._session = value

#     @property
#     def instances(self):
#         return self._instances

#     def seed(self, instance, add_to_session=True):
#         # validate
#         validator.SchemaValidator.validate(instance)

#         # clear previously generated objects
#         self._instances.clear()
#         self._class_registry.clear()

#         self._pre_seed(instance)

#         if add_to_session is True:
#             self._session.add_all(self.instances)

#     def _pre_seed(self, instance, parent=None, parent_attr_name=None):
#         if isinstance(instance, list):
#             for i in instance:
#                 self._seed(i, parent, parent_attr_name)
#         else:
#             self._seed(instance, parent, parent_attr_name)

#     def _seed(self, instance: dict, parent=None, parent_attr_name=None):
#         keys = None
#         for r_keys in self._required_keys:
#             if all(key in instance.keys() for key in r_keys):
#                 keys = r_keys
#                 break

#         if keys is None:
#             raise KeyError(
#                 "'filter' key is not allowed. Use HybridSeeder instead.")

#         key_is_data = keys[1] == "data"

#         class_path = instance[keys[0]]
#         self._class_registry.register_class(class_path)

#         if isinstance(instance[keys[1]], list):
#             for value in instance[keys[1]]:
#                 obj = self.instantiate_obj(class_path, value, key_is_data,
#                                            parent, parent_attr_name)
#                 # print(obj, parent, parent_attr_name)
#                 if parent is not None and parent_attr_name is not None:
#                     attr_ = getattr(parent.__class__, parent_attr_name)
#                     if isinstance(attr_.property, RelationshipProperty):
#                         if attr_.property.uselist is True:
#                             if getattr(parent, parent_attr_name) is None:
#                                 setattr(parent, parent_attr_name, [])

#                             getattr(parent, parent_attr_name).append(obj)
#                         else:
#                             setattr(parent, parent_attr_name, obj)
#                     else:
#                         setattr(parent, parent_attr_name, obj)
#                 else:
#                     if inspect(obj.__class__) and key_is_data is True:
#                         self._instances.append(obj)
#                 # check for relationships
#                 for k, v in value.items():
#                     if str(k).startswith("!"):
#                         self._pre_seed(v, obj, k[1:])  # removed prefix

#         elif isinstance(instance[keys[1]], dict):
#             obj = self.instantiate_obj(class_path, instance[keys[1]],
#                                        key_is_data, parent, parent_attr_name)
#             # print(parent, parent_attr_name)
#             if parent is not None and parent_attr_name is not None:
#                 attr_ = getattr(parent.__class__, parent_attr_name)
#                 if isinstance(attr_.property, RelationshipProperty):
#                     if attr_.property.uselist is True:
#                         if getattr(parent, parent_attr_name) is None:
#                             setattr(parent, parent_attr_name, [])

#                         getattr(parent, parent_attr_name).append(obj)
#                     else:
#                         setattr(parent, parent_attr_name, obj)
#                 else:
#                     setattr(parent, parent_attr_name, obj)
#             else:
#                 if inspect(obj.__class__) and key_is_data is True:
#                     self._instances.append(obj)

#             # check for relationships
#             for k, v in instance[keys[1]].items():
#                 # print(k, v)
#                 if str(k).startswith("!"):
#                     # print(k)
#                     self._pre_seed(v, obj, k[1:])  # removed prefix '!'

#         return instance

#     def instantiate_obj(self,
#                         class_path,
#                         kwargs,
#                         key_is_data,
#                         parent=None,
#                         parent_attr_name=None):
#         class_ = self._class_registry[class_path]

#         filtered_kwargs = {
#             k: v
#             for k, v in kwargs.items() if not k.startswith("!")
#             and not isinstance(getattr(class_, k), RelationshipProperty)
#         }

#         if key_is_data is True:
#             return class_(**filtered_kwargs)
#         else:
#             raise KeyError("key is invalid")


# class HybridSeeder(Seeder):
#     def __init__(self, session: sqlalchemy.orm.Session):
#         super().__init__(session=session)
#         self._required_keys = [("model", "data"), ("model", "filter")]

#     def seed(self, instance):
#         super().seed(instance, False)

#     def instantiate_obj(self,
#                         class_path,
#                         kwargs,
#                         key_is_data,
#                         parent=None,
#                         parent_attr_name=None):
#         """Instantiates or queries object, or queries ForeignKey

#         Args:
#             class_path (str): Class path
#             kwargs ([dict]): Class kwargs
#             key_is_data (bool): key is 'data'
#             parent (object): parent object
#             parent_attr_name (str): parent attribute name

#         Returns:
#             Any: instantiated object or queried object, or foreign key id
#         """

#         class_ = self._class_registry[class_path]

#         filtered_kwargs = {
#             k: v
#             for k, v in kwargs.items() if not k.startswith("!")
#             and not isinstance(getattr(class_, k), RelationshipProperty)
#         }

#         if key_is_data is True:
#             if parent is not None and parent_attr_name is not None:
#                 class_attr = getattr(parent.__class__, parent_attr_name)
#                 if isinstance(class_attr.property, ColumnProperty):
#                     raise TypeError("invalid class attribute type")

#             obj = class_(**filtered_kwargs)
#             self._session.add(obj)
#             # self._session.flush()
#             return obj
#         else:
#             if parent is not None and parent_attr_name is not None:
#                 class_attr = getattr(parent.__class__, parent_attr_name)
#                 if isinstance(class_attr.property, ColumnProperty):
#                     foreign_key = str(
#                         list(
#                             getattr(parent.__class__,
#                                     parent_attr_name).foreign_keys)[0].column)
#                     foreign_key_id = self._query_instance_id(
#                         class_, filtered_kwargs, foreign_key)
#                     return foreign_key_id

#             return self._session.query(class_).filter_by(
#                 **filtered_kwargs).one()

#     def _query_instance_id(self, class_, filtered_kwargs, foreign_key):
#         arr = foreign_key.rsplit(".")
#         column_name = arr[len(arr) - 1]

#         result = (self.session.query(getattr(
#             class_, column_name)).filter_by(**filtered_kwargs).one())
#         return getattr(result, column_name)

class Seeder:
    pass


class HybridSeeder:
    pass


# Entity = namedtuple("Entity", ["instance", "class_attribute"])

class Entity(NamedTuple):
    instance: object
    attr_name: str

    @property
    def cls_attr(self):
        return getattr(self.instance.__class__, self.attr_name)

    @property
    def ins_attr(self):
        return getattr(self.instance, self.attr_name)

    @ins_attr.setter
    def ins_attr(self, value):
        setattr(self.instance, self.attr_name, value)


def get_class_path(class_):
    return "{}.{}".format(class_.__module__, class_.__name__)


def instantiate_class(class_, kwargs: dict, key: validator.Key, parent: Entity, session: sqlalchemy.orm.Session = None):
    filtered_kwargs = {
        k: v
        for k, v in kwargs.items()
        if not k.startswith("!")
        and not isinstance(getattr(class_, k), RelationshipProperty)
    }

    if key is validator.Key.data():
        return class_(**filtered_kwargs)
    else:
        return


def set_instance_parent(instance, parent: Entity):
    if isinstance(parent.cls_attr.property, RelationshipProperty):
        if parent.cls_attr.property.uselist is True:
            if parent.ins_attr is not None:
                parent.ins_attr = []
            parent.ins_attr.append(instance)
        else:
            parent.ins_attr = instance


class FutureHybridSeeder:
    __model_key = validator.Key.model()
    __source_keys = validator.Key.source_keys()

    def __init__(self, session: sqlalchemy.orm.Session = None, ref_prefix="!"):
        self._session = session
        self._class_registry = ClassRegistry()
        self._instances = []
        self._ref_prefix = ref_prefix

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if not isinstance(value, sqlalchemy.orm.Session):
            raise TypeError("value type is not 'Session'.")

        self._session = value

    @property
    def instances(self):
        return tuple(self._instances)

    def get_model_class(self, entity, parent: Entity):
        model_label = self.__model_key.label
        if model_label in entity:
            class_path = entity[model_label]
            return self._class_registry.register_class(class_path)
        # parent is not None
        if isinstance(parent.attribute.property, RelationshipProperty):
            return parent.attribute.mapper.class_
        else:  # parent.attribute is instance of ColumnProperty
            table_name = parent.attribute.foreign_keys[0].table.name
            class_ = next(
                (mapper.class_
                 for mapper in parent.instance.__class__.registry.mappers
                 if mapper.class_.__tablename__ == table_name),
                errors.ClassNotFoundError(
                    "A class with table name '{}' is not found in the mappers".format(table_name)),
            )
            return class_

    def seed(self, entities):
        validator.SchemaValidator.validate(
            entities, ref_prefix=self._ref_prefix)

        self._pre_seed(entities)

    def _pre_seed(self, entity):
        if isinstance(entity, dict):
            self._seed(entity)
        else:
            for item in entity:
                self._seed(item)

    def _seed(self, entity, parent: Entity = None):
        class_ = self.get_model_class(entity, parent)
        source_key: validator.Key = next(
            (sk for sk in self.__source_keys if sk.label in entity), None)
        source_data = entity[source_key.label]
        if isinstance(source_data, dict):
            # instantiate object
            instance = instantiate_class(
                class_, source_data, source_key, parent)
        else:  # source_data is list
            pass


if __name__ == "__main__":
    from tests.models import Company

    seeder = FutureHybridSeeder()
    print(seeder.instances)
