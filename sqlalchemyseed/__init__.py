import importlib
import json
from inspect import isclass

import pkg_resources
from jsonschema import validate

__version__ = '0.1.3'

_SCHEMA_PATH = './schema.json'


def validate_entities(entities):
    schema_res = pkg_resources.resource_string('sqlalchemyseed', _SCHEMA_PATH)
    schema = json.loads(schema_res)

    validate(entities, schema)


def load_entities_from_json(json_filepath):
    try:
        with open(json_filepath, 'r') as f:
            entities = json.loads(f.read())
    except FileNotFoundError as error:
        raise FileNotFoundError(error)

    return entities


class _ClassRegistry:
    def __init__(self):
        self._classes = {}
        self._modules = {}

    def register_class(self, class_path: str):
        try:
            module_name, class_name = class_path.rsplit('.', 1)
        except ValueError:
            raise ValueError('Invalid module or class input format.')

        if module_name not in self._modules:
            self._modules[module_name] = importlib.import_module(module_name)

        if class_name not in self._classes:
            class_ = getattr(self._modules[module_name], class_name)

            if isclass(class_):
                self._classes[class_name] = class_
            else:
                raise TypeError("'{}' is not a class".format(class_name))

    def get_class(self, class_path: str):
        try:
            class_name = class_path.rsplit('.', 1)[1]
        except IndexError:
            class_name = class_path

        return self._classes[class_name]

    def registered_classes(self):
        return self._classes.values()

    def clear(self):
        self._classes.clear()


class Seeder:
    def __init__(self):
        self.class_registry = _ClassRegistry()
        self.object_instances = []

    def seed(self, entities, session=None):
        validate_entities(entities)
        self.object_instances.clear()

        if isinstance(entities, dict):
            self._entity(entities)
        elif isinstance(entities, list):
            self._entities(entities)

        if session:
            session.add_all(self.object_instances)

    def _entity(self, entity, parent=None):
        class_path = entity['model']
        data, data_key = self._get_data(entity)

        self.class_registry.register_class(class_path)

        if isinstance(data, dict):
            return self._field(data, class_path, parent, data_key)
        elif isinstance(data, list):
            self._fields(data, class_path, parent, data_key)

    @staticmethod
    def _get_data(entity):
        key = 'data'
        return entity[key], key

    def _entities(self, entities):
        for entity in entities:
            self._entity(entity)

    def _create_instance(self, field, class_path, data_key):
        kwargs_ = {k: v for k, v in field.items() if not isinstance(v, dict) and not isinstance(v, list)}
        class_ = self.class_registry.get_class(class_path)

        return class_(**kwargs_)

    def _field(self, field: dict, class_path: str, parent=None, data_key=None):

        instance = self._create_instance(field, class_path, data_key)

        if parent is None:
            self.object_instances.append(instance)
            parent = instance

        for parent_key, value in field.items():
            if isinstance(value, dict):
                child = self._entity(value, parent=parent)
                setattr(parent, parent_key, child)
            elif isinstance(value, list):
                children = []
                for i in value:
                    children.append(
                        self._entity(i, parent=parent)
                    )
                setattr(parent, parent_key, children)

        return instance

    def _fields(self, fields, model: str, parent=None, data_key=None):
        for field in fields:
            self._field(field, model, parent=parent, data_key=data_key)


class HybridSeeder(Seeder):
    def __init__(self, session, auto_add=True):
        super().__init__()
        if session is None:
            raise ValueError('session not found.')
        self.session = session
        self.auto_add = auto_add

    def seed(self, entities, session=None):
        super().seed(entities, self.session)

    def _get_data(self, entity):
        try:
            return super()._get_data(entity)
        except KeyError:
            key = 'filter'
            return entity[key], key

    def _create_instance(self, field, class_path, data_key):
        if data_key == 'data':
            instance = super()._create_instance(field, class_path, data_key)
            if self.auto_add:
                self.session.add(instance)
            return instance
        else:
            class_ = self.class_registry.get_class(class_path)
            return self.session.query(class_).filter_by(
                **{k: v for k, v in field if not isinstance(v, dict) and not isinstance(v, list)}
            ).one_or_none()


# ----------------------------------------------------------------------------------------------------------------------
def is_dict(data):
    return isinstance(data, dict)


def is_list(data):
    return isinstance(data, list)


# class Schema:
#
#     def __init__(self):
#         self.class_registry = _ClassRegistry()
#         self.instances = []
#
#     def create(self, data):
#         validate_entities(data)
#         self.instances.clear()
#
#         self.root(data)
#
#     def root(self, data):
#         if is_dict(data):
#             instance = self._entity(data)
#             return self.instances.append(instance)
#         elif is_list(data):
#             return self.instances.append(self._entities(data, []))
#
#     def _entities(self, data: list, array):
#         mid = len(data) // 2
#         left = data[:mid]
#         right = data[mid:]
#
#         if len(data) == 1:
#             instance = self._entity(data[0])
#             array.append(instance)
#             return array
#
#         self._entities(left, array)
#         self._entities(right, array)
#
#     def _create_instance(self, data: dict, class_path: str):
#         kwargs = {k: v for k, v in data.items() if not is_dict(v) and not is_list(v)}
#
#         class_ = self.class_registry.get_class(class_path)
#         return class_(**kwargs)
#
#     def _entity(self, data: dict):
#         model_key, data_key = data.keys()
#
#         self.class_registry.register_class(data[model_key])
#         self._current_class_path = data[model_key]
#
#         return self._args(data[data_key], data[model_key])
#
#     def _args(self, data, class_path):
#         # traversing the data
#         if is_dict(data):
#             return self._field(data, class_path)
#         elif is_list(data):
#             return self._fields(data, class_path)
#
#     def _fields(self, data: dict, class_path):
#         # return [self._field(item, class_path) for item in data]
#
#         mid = len(data) // 2
#         left = data[:mid]
#         right = data[mid:]
#
#         if len(data) == 1:
#             # print('fields recursion ------------------')
#             return self._field(data[0], class_path)
#
#         self._fields(left, class_path)
#         self._fields(right, class_path)
#
#     def _field(self, data: dict, class_path):
#         # print('next --------------')
#         # print(data)
#         instance = self._create_instance(data, class_path)
#         # print(instance)
#         # print('end- ----------------')
#
#         # check for child or children
#         for key, item in data.items():
#             if is_dict(item):
#                 child_instance = self._entity(item)
#                 setattr(instance, key, child_instance)
#
#             elif is_list(item):
#                 print(item)
#                 child_instances = self._entities(item, [])
#                 print(child_instances)
#                 setattr(instance, key, child_instances)
#
#         return instance


# class BasicSeeder:
#     def __init__(self):
#         self.class_registry = _ClassRegistry()
#         self.instances = []
#         self.depth = 0
#
#     def _create_instance(self, data: dict, class_path: str):
#         kwargs = {k: v for k, v in data.items() if not is_dict(v) and not is_list(v)}
#
#         class_ = self.class_registry.get_class(class_path)
#         instance = class_(**kwargs)
#
#         self.instance_attributes(instance, data)
#
#         return instance
#
#     def root(self, data):
#         validate_entities(data)
#         self.instances.clear()
#         # type object
#         if isinstance(data, dict):
#             self.entity(data)
#         # type array
#         elif isinstance(data, list):
#             self.group_entity(data)
#         else:
#             raise ValueError("Value is neither dict nor list.")
#
#     def entity(self, data):
#         keys = list(data.keys())
#         # anyOf
#         required = [
#             ('model', 'data'),
#             ('model', 'filter')
#         ]
#         valid_keys = False
#         for require in required:
#             if all(i in require for i in keys):
#                 valid_keys = True
#                 keys = require
#                 break
#
#         if valid_keys is False:
#             # create instance
#             raise KeyError(f"keys: {keys} not complying the required")
#
#         class_path, sub_data = data[keys[0]], data[keys[1]]
#
#         self.class_registry.register_class(class_path)
#
#         if isinstance(sub_data, dict):
#             return self.entity_data(sub_data, class_path)
#
#         elif isinstance(sub_data, list):
#             self.entity_group_data(sub_data, class_path)
#         else:
#             raise TypeError("data is neither 'dict' nor 'list'")
#
#     def entity_data(self, data, class_path):
#         return self._create_instance(data, class_path)
#
#     def entity_group_data(self, data, class_path):
#         # for item in data:
#         #     self.entity_data(item, class_path)
#         # [self.entity_data(item, class_path) for item in data]
#         mid = len(data) // 2
#         left = data[:mid]
#         right = data[mid:]
#
#         if len(data) == 1:
#             self.entity_data(data[0], class_path)
#             return
#
#         self.entity_group_data(left, class_path)
#         self.entity_group_data(right, class_path)
#
#     def instance_attributes(self, instance, data):
#         self.depth += 1
#         if self.depth == 1:
#             self.instances.append(instance)
#
#         # children
#         for key, item in data.items():
#             if isinstance(item, dict):
#                 child = self.instance_child(item)
#                 setattr(instance, key, child)
#             elif isinstance(item, list):
#                 children = self.instance_children(item)
#                 setattr(instance, key, children)
#
#         self.depth -= 1
#
#     def instance_child(self, data):
#         return self.entity(data)
#
#     def instance_children(self, data):
#         return [self.instance_child(item) for item in data]
#
#     def group_entity(self, data):
#         mid = len(data) // 2
#         left = data[:mid]
#         right = data[mid:]
#
#         if len(data) == 1:
#             return self.entity(data[0])
#
#         self.group_entity(left)
#         self.group_entity(right)
#
#
# class SuperSeeder(BasicSeeder):
#     def __init__(self, session):
#         super().__init__()
#         self.session = session
