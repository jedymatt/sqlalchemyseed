import abc
import importlib
import json
from inspect import isclass

import pkg_resources
from jsonschema import validate
from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

__version__ = '0.3.0-dev1'

__SCHEMA_PATH = 'res/schema.json'


def validate_entities(entities):
    schema_res = pkg_resources.resource_string('sqlalchemyseed', __SCHEMA_PATH)
    schema = json.loads(schema_res)

    validate(entities, schema)


def load_entities_from_json(json_filepath):
    try:
        with open(json_filepath, 'r') as f:
            entities = json.loads(f.read())
    except FileNotFoundError as error:
        raise FileNotFoundError(error)

    validate_entities(entities)

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


class Seeder:
    def __init__(self, session=None):
        self._class_registry = ClassRegistry()
        self.session = session
        self._instances = []
        self._depth = 0

        self.required_keys = [
            ('model', 'data')
        ]

    @property
    def instances(self):
        return self._instances

    def seed(self, entities, add_to_session=True):
        validate_entities(entities)

        if len(self._instances) > 0:
            self._instances.clear()

        if len(self._class_registry.registered_classes) > 0:
            self._class_registry.clear()

        self._root(entities)

        if add_to_session is True:
            if self.session is None:
                raise ValueError(
                    'Session is None: Cannot add instances to session')
            self.session.add_all(self.instances)

    @abc.abstractmethod
    def _load_instance(self, class_, kwargs, keys):
        return class_(**kwargs)

    @abc.abstractmethod
    def _add_to_session(self, instance):
        pass

    def _create_instance(self, data: dict, class_path: str, keys):
        kwargs = {k: v for k, v in data.items() if not isinstance(
            v, dict) and not isinstance(v, list)}

        class_ = self._class_registry[class_path]
        instance = self._load_instance(class_, kwargs, keys)

        self._depth += 1
        if self._depth == 1:
            self._instances.append(instance)
            self._add_to_session(instance)

        # find child or children in its attribute
        for key, item in data.items():
            if isinstance(item, dict):
                child = self._create_instance_child(item)
                setattr(instance, key, child)
            elif isinstance(item, list):
                children = self._create_instance_children(item)
                setattr(instance, key, children)

        self._depth -= 1

        return instance

    def _root(self, data):
        # type object
        if isinstance(data, dict):
            self._entity(data)
        # type array
        elif isinstance(data, list):
            self._group_entity(data)
        else:
            raise ValueError("Value is neither dict nor list.")

    def _entity(self, data):
        keys = list(data.keys())
        # anyOf
        valid_keys = False
        for require in self.required_keys:
            if all(i in require for i in keys):
                valid_keys = True
                keys = require
                break

        if valid_keys is False:
            # create instance
            raise KeyError(f"Invalid Keys: {keys} not complying the required")

        class_path, sub_data = data[keys[0]], data[keys[1]]

        self._class_registry.register_class(class_path)

        if isinstance(sub_data, dict):
            return self._entity_data(sub_data, class_path, keys)

        elif isinstance(sub_data, list):
            self._entity_group_data(sub_data, class_path, keys)
        else:
            raise TypeError("data is neither 'dict' nor 'list'")

    def _entity_data(self, data, class_path, keys):
        return self._create_instance(data, class_path, keys)

    def _entity_group_data(self, data, class_path, keys):
        # for item in data:
        #     self.entity_data(item, class_path)
        # [self.entity_data(item, class_path) for item in data]
        mid = len(data) // 2
        left = data[:mid]
        right = data[mid:]

        if len(data) == 1:
            self._entity_data(data[0], class_path, keys)
            return

        self._entity_group_data(left, class_path, keys)
        self._entity_group_data(right, class_path, keys)

    def _create_instance_child(self, data):
        return self._entity(data)

    def _create_instance_children(self, data):
        return [self._create_instance_child(item) for item in data]

    def _group_entity(self, data):
        mid = len(data) // 2
        left = data[:mid]
        right = data[mid:]

        if len(data) == 1:
            return self._entity(data[0])

        self._group_entity(left)
        self._group_entity(right)


class HybridSeeder(Seeder):

    def __init__(self, session):
        super().__init__(session)
        self.required_keys = [
            ('model', 'data'),
            ('model', 'filter')
        ]

    def seed(self, entities, **kwargs):
        super().seed(entities, False)

    def _load_instance(self, class_, kwargs, keys):
        if keys[1] == 'data':
            return class_(**kwargs)
        else:  # keys[1] == 'filter'
            return self.session.query(class_).filter_by(**kwargs).one_or_none()

    def _add_to_session(self, instance):
        self.session.add(instance)
