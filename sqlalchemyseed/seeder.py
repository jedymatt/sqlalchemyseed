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


class Seeder:
    def __init__(self, session: sqlalchemy.orm.Session = None):
        self._session = session
        self._class_registry = ClassRegistry()
        self._instances = []

        self._required_keys = [
            ('model', 'data')
        ]

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if not isinstance(value, sqlalchemy.orm.Session):
            raise TypeError("obj type is not 'Session'.")

        self._session = value

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
            self._session.add_all(self.instances)

    def _pre_seed(self, instance, parent=None, parent_attr=None):
        if isinstance(instance, list):
            for i in instance:
                self._seed(i, parent, parent_attr)
        else:
            self._seed(instance, parent, parent_attr)

    def _seed(self, instance: dict, parent=None, parent_attr=None):
        keys = None
        for r_keys in self._required_keys:
            if all(key in instance.keys() for key in r_keys):
                keys = r_keys
                break

        if keys is None:
            raise KeyError(
                "'filter' key is not allowed. Use HybridSeeder instead.")

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
            obj = self.instantiate_obj(
                class_path, instance[keys[1]], key_is_data)
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
        self._required_keys = [
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
            self._session.add(obj)
            return obj
        else:
            return self._session.query(class_).filter_by(**filtered_kwargs).one()
