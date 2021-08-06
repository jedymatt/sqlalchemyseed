import importlib
import json
from inspect import isclass

import sqlalchemy.orm
from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import RelationshipProperty

from . import validator


def load_entities_from_json(json_filepath):
    try:
        with open(json_filepath, 'r') as f:
            entities = json.loads(f.read())
    except FileNotFoundError as error:
        raise FileNotFoundError(error)

    validator.SchemaValidator.validate(entities)

    return entities


class ClassRegistry:
    def __init__(self):
        self._classes = {}

    def register_class(self, class_path: str):
        try:
            module_name, class_name = class_path.rsplit('.', 1)
        except ValueError:
            raise ValueError('Invalid module or class input format.')

        if class_name not in self._classes:
            class_ = getattr(importlib.import_module(module_name), class_name)

            try:
                if isclass(class_) and inspect(class_):
                    self._classes[class_path] = class_
                else:
                    raise TypeError("'{}' is not a class".format(class_name))
            except NoInspectionAvailable:
                raise TypeError(
                    "'{}' is an unsupported class".format(class_name))

    def __getitem__(self, class_path: str):
        return self._classes[class_path]

    @property
    def registered_classes(self):
        return self._classes.values()

    def clear(self):
        self._classes.clear()


# class Seeder:
#     def __init__(self, session=None):
#         self._class_registry = ClassRegistry()
#         self.session = session
#         self._instances = []
#         self._depth = 0

#         self.required_keys = [
#             ('model', 'obj')
#         ]

#     @property
#     def instances(self):
#         return self._instances

#     def seed(self, entities, add_to_session=True):
#         validate_entities(entities)

#         if len(self._instances) > 0:
#             self._instances.clear()

#         if len(self._class_registry.registered_classes) > 0:
#             self._class_registry.clear()

#         self._root(entities)

#         if add_to_session is True:
#             if self.session is None:
#                 raise ValueError(
#                     'Session is None: Cannot add instances to session')
#             self.session.add_all(self.instances)

#     @abc.abstractmethod
#     def _load_instance(self, class_, kwargs, keys):
#         return class_(**kwargs)

#     @abc.abstractmethod
#     def _add_to_session(self, instance):
#         pass

#     def _create_instance(self, obj: dict, class_path: str, keys):
#         kwargs = {k: v for k, v in obj.items() if not isinstance(
#             v, dict) and not isinstance(v, list)}

#         class_ = self._class_registry[class_path]
#         instance = self._load_instance(class_, kwargs, keys)

#         self._depth += 1
#         if self._depth == 1:
#             self._instances.append(instance)
#             self._add_to_session(instance)

#         # find child or children in its attribute
#         for key, item in obj.items():
#             if isinstance(item, dict):
#                 child = self._create_instance_child(item)
#                 setattr(instance, key, child)
#             elif isinstance(item, list):
#                 children = self._create_instance_children(item)
#                 setattr(instance, key, children)

#         self._depth -= 1

#         return instance

#     def _root(self, obj):
#         # type object
#         if isinstance(obj, dict):
#             self._entity(obj)
#         # type array
#         elif isinstance(obj, list):
#             self._group_entity(obj)
#         else:
#             raise ValueError("Value is neither dict nor list.")

#     def _entity(self, obj):
#         keys = list(obj.keys())
#         # anyOf
#         valid_keys = False
#         for require in self.required_keys:
#             if all(i in require for i in keys):
#                 valid_keys = True
#                 keys = require
#                 break

#         if valid_keys is False:
#             # create instance
#             raise KeyError(f"Invalid Keys: {keys} not complying the required")

#         class_path, sub_data = obj[keys[0]], obj[keys[1]]

#         self._class_registry.register_class(class_path)

#         if isinstance(sub_data, dict):
#             return self._entity_data(sub_data, class_path, keys)

#         elif isinstance(sub_data, list):
#             self._entity_group_data(sub_data, class_path, keys)
#         else:
#             raise TypeError("obj is neither 'dict' nor 'list'")

#     def _entity_data(self, obj, class_path, keys):
#         return self._create_instance(obj, class_path, keys)

#     def _entity_group_data(self, obj, class_path, keys):
#         # for item in obj:
#         #     self.entity_data(item, class_path)
#         # [self.entity_data(item, class_path) for item in obj]
#         mid = len(obj) // 2
#         left = obj[:mid]
#         right = obj[mid:]

#         if len(obj) == 1:
#             self._entity_data(obj[0], class_path, keys)
#             return

#         self._entity_group_data(left, class_path, keys)
#         self._entity_group_data(right, class_path, keys)

#     def _create_instance_child(self, obj):
#         return self._entity(obj)

#     def _create_instance_children(self, obj):
#         return [self._create_instance_child(item) for item in obj]

#     def _group_entity(self, obj):
#         mid = len(obj) // 2
#         left = obj[:mid]
#         right = obj[mid:]

#         if len(obj) == 1:
#             return self._entity(obj[0])

#         self._group_entity(left)
#         self._group_entity(right)


# class HybridSeeder(Seeder):

#     def __init__(self, session):
#         super().__init__(session)
#         self.required_keys = [
#             ('model', 'obj'),
#             ('model', 'filter')
#         ]

#     def seed(self, entities, **kwargs):
#         super().seed(entities, False)

#     def _load_instance(self, class_, kwargs, keys):
#         if keys[1] == 'obj':
#             return class_(**kwargs)
#         else:  # keys[1] == 'filter'
#             return self.session.query(class_).filter_by(**kwargs).one_or_none()

#     def _add_to_session(self, instance):
#         self.session.add(instance)


# class DataSeek:
#     def __init__(self):
#         self.root = '/'
#         self.current_path = self.root
#
#     @staticmethod
#     def parse_address(path: str):
#         return list(
#             [int(x) if x.isdecimal() else x for x in path.split('/') if x != '' and x is not None]
#         )
#
#     def get_data(self, data, path: str):
#         if path.startswith('/'):
#             path = path[1:]
#
#         # parse
#         address = self.parse_address(path)
#
#         current_data = data
#         for idx in address:
#             if isinstance(current_data, str):
#                 raise TypeError("'str' object is restricted in indexing and slicing")
#             current_data = current_data[idx]
#         return current_data
#
#     def traverse(self, data):
#         if isinstance(data, dict):
#             pass
#         elif isinstance(data, list):
#             pass


class Seeder:
    def __init__(self, session: sqlalchemy.orm.Session = None):
        self.session = session
        self._class_registry = ClassRegistry()
        self._instances = []

        self.required_keys = [
            ('model', 'data')
        ]

    @property
    def instances(self):
        return self._instances

    def seed(self, instance, add_to_session=True):
        # validate
        validator.SchemaValidator.validate(instance)

        # clear previously generated objects
        self._instances.clear()
        self._class_registry.clear()

        self._pre_seed(instance)

        if add_to_session is True:
            self.session.add_all(self.instances)

    def _pre_seed(self, instance, parent=None, parent_attr=None):
        if isinstance(instance, list):
            for i in instance:
                self._seed(i, parent, parent_attr)
        else:
            self._seed(instance, parent, parent_attr)

    def _seed(self, instance: dict, parent=None, parent_attr=None):
        keys = None
        for r_keys in self.required_keys:
            if all(key in instance.keys() for key in r_keys):
                keys = r_keys
                break

        if keys is None:
            raise KeyError("'filter' key is not allowed. Use HybridSeeder instead.")

        key_is_data = keys[1] == 'data'

        class_path = instance[keys[0]]
        self._class_registry.register_class(class_path)

        if isinstance(instance[keys[1]], list):
            for value in instance[keys[1]]:
                obj = self.instantiate_obj(class_path, value, key_is_data)
                # print(obj, parent, parent_attr)
                if parent is not None and parent_attr is not None:
                    attr_ = getattr(parent.__class__, parent_attr)
                    if attr_.property.uselist is True:
                        if getattr(parent, parent_attr) is None:
                            setattr(parent, parent_attr, [])

                        getattr(parent, parent_attr).append(obj)
                    else:
                        setattr(parent, parent_attr, obj)
                else:
                    self._instances.append(obj)
                # check for relationships
                for k, v in value.items():
                    if str(k).startswith('!'):
                        self._pre_seed(v, obj, k[1:])

        elif isinstance(instance[keys[1]], dict):
            obj = self.instantiate_obj(class_path, instance[keys[1]], key_is_data)
            # print(parent, parent_attr)
            if parent is not None and parent_attr is not None:
                attr_ = getattr(parent.__class__, parent_attr)
                if attr_.property.uselist is True:
                    if getattr(parent, parent_attr) is None:
                        setattr(parent, parent_attr, [])

                    getattr(parent, parent_attr).append(obj)
                else:
                    setattr(parent, parent_attr, obj)
            else:
                self._instances.append(obj)
            # check for relationships
            for k, v in instance[keys[1]].items():
                # print(k, v)
                if str(k).startswith('!'):
                    # print(k)
                    self._pre_seed(v, obj, k[1:])

        return instance

    def instantiate_obj(self, class_path, kwargs, key_is_data):
        class_ = self._class_registry[class_path]

        filtered_kwargs = {k: v for k, v in kwargs.items() if
                           not k.startswith('!') and not isinstance(getattr(class_, k), RelationshipProperty)}

        if key_is_data is True:
            return class_(**filtered_kwargs)
        else:
            raise KeyError("key is invalid")


class HybridSeeder(Seeder):
    def __init__(self, session: sqlalchemy.orm.Session):
        super().__init__(session=session)
        self.required_keys = [
            ('model', 'data'),
            ('model', 'filter')
        ]

    def seed(self, instance, **kwargs):
        super().seed(instance, False)

    def instantiate_obj(self, class_path, kwargs, key_is_data=True):
        class_ = self._class_registry[class_path]

        filtered_kwargs = {k: v for k, v in kwargs.items() if
                           not k.startswith('!') and not isinstance(getattr(class_, k), RelationshipProperty)}

        if key_is_data is True:
            obj = class_(**filtered_kwargs)
            self.session.add(obj)
            return obj
        else:
            return self.session.query(class_).filter_by(**filtered_kwargs).one()
