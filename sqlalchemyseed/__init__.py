import importlib
import json
from inspect import isclass

import pkg_resources
from jsonschema import validate

__version__ = '0.1.1'

_SCHEMA_PATH = 'schema.json'


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

    validate_entities(entities)
    return entities


class _ClassRegistry:
    def __init__(self):
        self._classes = {}
        self._modules = {}

    def register_class(self, class_path):
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

    def get_class(self, class_path):
        try:
            class_name = class_path.rsplit('.', 1)[1]
        except IndexError:
            class_name = class_path

        return self._classes[class_name]


class Seeder:
    def __init__(self):
        self.class_registry = _ClassRegistry()
        self.object_instances = []

    def seed(self, entities, session=None):
        validate_entities(entities)
        self.object_instances = []

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

        instance = None

        if isinstance(data, dict):
            instance = self._field(data, class_path, parent, data_key)
        elif isinstance(data, list):
            self._fields(data, class_path, parent, data_key)

        return instance

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
