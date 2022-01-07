"""
Seeder module
"""

import abc
from types import FunctionType, LambdaType
from typing import Any, Callable, Iterable, NamedTuple
from sqlalchemyseed.constants import MODEL_KEY, DATA_KEY

import sqlalchemy
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql import schema

from sqlalchemyseed.json import JsonWalker

from . import class_registry, validator, errors, util


class AbstractSeeder(abc.ABC):
    """
    AbstractSeeder class
    """

    @property
    @abc.abstractmethod
    def instances(self):
        """
        Seeded instances
        """

    @abc.abstractmethod
    def seed(self, entities):
        """
        Seed data
        """

    @abc.abstractmethod
    def _pre_seed(self, *args, **kwargs):
        """
        Pre-seeding phase
        """

    @abc.abstractmethod
    def _seed(self, *args, **kwargs):
        """
        Seeding phase
        """

    @abc.abstractmethod
    def _seed_children(self, *args, **kwargs):
        """
        Seed children
        """

    @abc.abstractmethod
    def _setup_instance(self, *args, **kwargs):
        """
        Setup instance
        """


class EntityTuple(NamedTuple):
    instance: object
    attr_name: str


class Entity(EntityTuple):
    @property
    def class_attribute(self):
        print(type(getattr(self.instance.__class__, self.attr_name)))
        return getattr(self.instance.__class__, self.attr_name)

    @property
    def instance_attribute(self):
        return getattr(self.instance, self.attr_name)

    @instance_attribute.setter
    def instance_attribute(self, value):
        setattr(self.instance, self.attr_name, value)

    def is_column_attribute(self):
        return isinstance(self.class_attribute.property, ColumnProperty)

    def is_relationship_attribute(self):
        return isinstance(self.class_attribute.property, RelationshipProperty)

    @property
    def referenced_class(self):
        if self.is_relationship_attribute():
            return self.class_attribute.mapper.class_

        # if self.is_column_attribute():
        table_name = get_foreign_key_column(self.class_attribute).table.name

        return next(filter(
            lambda mapper: mapper.class_.__tablename__ == table_name,
            object_mapper(self.instance).registry.mappers
        )).class_


def get_foreign_key_column(attr, idx=0) -> schema.Column:
    return list(attr.foreign_keys)[idx].column


def filter_kwargs(kwargs: dict, class_, ref_prefix):
    return {
        k: v for k, v in util.iter_non_ref_kwargs(kwargs, ref_prefix)
        if not isinstance(getattr(class_, str(k)).property, RelationshipProperty)
    }


def set_parent_attr_value(instance, parent: Entity):
    if parent.is_relationship_attribute():
        if parent.class_attribute.property.uselist is True:
            parent.instance_attribute.append(instance)
        else:
            parent.instance_attribute = instance

    else:  # if parent.is_column_attribute():
        parent.instance_attribute = instance


class Seeder(AbstractSeeder):
    """
    Basic Seeder class
    """

    def __init__(self, session: sqlalchemy.orm.Session = None, ref_prefix="!"):
        self.session = session
        self._class_registry = class_registry.ClassRegistry()
        self._instances = []
        self.ref_prefix = ref_prefix
        self._json: JsonWalker = JsonWalker()

    @property
    def instances(self):
        return tuple(self._instances)

    def get_model_class(self, entity, parent: Entity):
        if MODEL_KEY.key in entity:
            return self._class_registry.register_class(entity[MODEL_KEY.key])
        # parent is not None
        return parent.referenced_class

    def seed(self, entities, add_to_session=True):
        validator.validate(entities=entities, ref_prefix=self.ref_prefix)

        self._instances.clear()
        self._class_registry.clear()

        self._json.reset(root=entities)

        self._pre_seed()

        if add_to_session:
            self.session.add_all(self.instances)

    def _pre_seed(self, parent=None):
        # iterates current json as list
        # expected json value is [{'model': ...}, ...]
        for _ in self._json.iter_as_list():
            self._seed(parent)

    def _seed(self,  parent: Entity = None):
        # expected json value is {'model': ..., 'data': ...}
        json = self._json.current
        class_ = self.get_model_class(json, parent)

        # moves json.current to json.current[self.__data_key]
        # expected json value is [{'value':...}]
        self._json.forward([DATA_KEY.key])
        # iterate json.current as list
        for kwargs in self._json.iter_as_list():
            instance = self._setup_instance(class_, kwargs, parent)
            self._seed_children(instance, kwargs)

        self._json.backward()

    def _seed_children(self, instance, kwargs):
        # expected json is dict:
        # {'model': ...}
        for key, _ in self._json.iter_as_dict_items():
            # key is equal to self._json.current_key

            if str(key).startswith(self.ref_prefix):
                attr_name = key[len(self.ref_prefix):]
                self._pre_seed(parent=Entity(instance, attr_name))

    def _setup_instance(self, class_, kwargs: dict, parent: Entity):
        instance = class_(**filter_kwargs(kwargs, class_, self.ref_prefix))
        if parent is not None:
            set_parent_attr_value(instance, parent)
        else:
            self._instances.append(instance)
        return instance


class HybridSeeder(AbstractSeeder):
    """
    HybridSeeder class. Accepts 'filter' key for referencing children.
    """
    __model_key = validator.Key.model()
    __source_keys = [validator.Key.data(), validator.Key.filter()]

    def __init__(self, session: sqlalchemy.orm.Session, ref_prefix: str = '!'):
        self.session = session
        self._class_registry = class_registry.ClassRegistry()
        self._instances = []
        self.ref_prefix = ref_prefix

    @property
    def instances(self):
        return tuple(self._instances)

    def get_model_class(self, entity, parent: Entity):
        # if self.__model_key in entity and (parent is not None and parent.is_column_attribute()):
        #     raise errors.InvalidKeyError("column attribute does not accept 'model' key")

        if self.__model_key in entity:
            class_path = entity[self.__model_key]
            return self._class_registry.register_class(class_path)

        # parent is not None
        return parent.referenced_class

    def seed(self, entities):
        validator.hybrid_validate(
            entities=entities, ref_prefix=self.ref_prefix)

        self._instances.clear()
        self._class_registry.clear()

        self._pre_seed(entities)

    def _pre_seed(self, entity, parent=None):
        if isinstance(entity, dict):
            self._seed(entity, parent)
        else:  # is list
            for item in entity:
                self._pre_seed(item, parent)

    def _seed(self, entity, parent):
        class_ = self.get_model_class(entity, parent)

        source_key = next(
            filter(lambda sk: sk in entity, self.__source_keys)
        )

        source_data = entity[source_key]

        # source_data is list
        if isinstance(source_data, list):
            for kwargs in source_data:
                instance = self._setup_instance(
                    class_, kwargs, source_key, parent)
                self._seed_children(instance, kwargs)
            return

        # source_data is dict
        instance = self._setup_instance(
            class_, source_data, source_key, parent)
        self._seed_children(instance, source_data)

    def _seed_children(self, instance, kwargs):
        for attr_name, value in util.iter_ref_kwargs(kwargs, self.ref_prefix):
            self._pre_seed(entity=value, parent=Entity(instance, attr_name))

    def _setup_instance(self, class_, kwargs: dict, key, parent):
        filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix)

        if key == key.data():
            instance = self._setup_data_instance(
                class_, filtered_kwargs, parent)
        else:  # key == key.filter()
            # instance = self.session.query(class_).filter_by(**filtered_kwargs)
            instance = self._setup_filter_instance(
                class_, filtered_kwargs, parent)

        # setting parent
        if parent is not None:
            set_parent_attr_value(instance, parent)

        return instance

    def _setup_data_instance(self, class_, filtered_kwargs, parent: Entity):
        if parent is not None and parent.is_column_attribute():
            raise errors.InvalidKeyError(
                "'data' key is invalid for a column attribute.")

        instance = class_(**filtered_kwargs)

        if parent is None:
            self.session.add(instance)
            self._instances.append(instance)

        return instance

    def _setup_filter_instance(self, class_, filtered_kwargs, parent: Entity):
        if parent is not None and parent.is_column_attribute():
            foreign_key_column = get_foreign_key_column(parent.class_attribute)
            return self.session.query(foreign_key_column).filter_by(**filtered_kwargs).one()[0]

        if parent is not None and parent.is_relationship_attribute():
            return self.session.query(parent.referenced_class).filter_by(**filtered_kwargs).one()

        return self.session.query(class_).filter_by(**filtered_kwargs).one()
