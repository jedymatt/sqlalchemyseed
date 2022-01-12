"""
Seeder module
"""

import abc
from typing import NamedTuple, Union

import sqlalchemy

from . import class_registry, errors, util, validator
from .attribute import (attr_is_column, attr_is_relationship, foreign_key_column, get_instrumented_attribute,
                        referenced_class, set_instance_attribute)
from .constants import DATA_KEY, MODEL_KEY
from .json import JsonWalker


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
    attr: str


# def get_foreign_key_column(attr) -> schema.Column:
#     return next(iter(attr.foreign_keys)).column


def filter_kwargs(kwargs: dict, class_, ref_prefix):
    return {
        k: v for k, v in util.iter_non_ref_kwargs(kwargs, ref_prefix)
        if not attr_is_relationship(get_instrumented_attribute(class_, str(k)))
    }


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

    def get_model_class(self, entity, parent: EntityTuple):
        if MODEL_KEY.key in entity:
            return self._class_registry.register_class(entity[MODEL_KEY.key])
        # parent is not None
        return referenced_class(get_instrumented_attribute(parent.instance, parent.attr))

    def seed(self, entities: Union[list, dict], add_to_session=True):
        validator.validate(entities=entities, ref_prefix=self.ref_prefix)

        self._instances.clear()
        self._class_registry.clear()
        self._parent = None

        self._json.reset(root=entities)

        self._pre_seed()

        if add_to_session:
            self.session.add_all(self.instances)

    def _pre_seed(self, parent=None):
        # iterates current json as list
        # expected json value is [{'model': ...}, ...]
        for _ in self._json.iter_as_list():
            self._seed(parent)

    def _seed(self, parent):
        # expected json value is {'model': ..., 'data': ...}
        json = self._json.current
        class_ = self.get_model_class(json, parent)

        # moves json.current to json.current[self.__data_key]
        # expected json value is [{'value':...}]
        self._json.forward([DATA_KEY.key])
        # iterate json.current as list
        for kwargs in self._json.iter_as_list():
            instance = self._setup_instance(class_, kwargs, parent)
            self._seed_children(instance)

        self._json.backward()

    def _seed_children(self, instance):
        # expected json is dict:
        # {'model': ...}
        for key, _ in self._json.iter_as_dict_items():
            # key is equal to self._json.current_key
            if str(key).startswith(self.ref_prefix):
                attr_name = key[len(self.ref_prefix):]
                self._pre_seed(parent=EntityTuple(instance, attr_name))

    def _setup_instance(self, class_, kwargs: dict, parent: EntityTuple):
        instance = class_(**filter_kwargs(kwargs, class_, self.ref_prefix))
        if parent is not None:
            set_instance_attribute(parent.instance, parent.attr, instance)
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

    def get_model_class(self, entity, parent: EntityTuple):
        # if self.__model_key in entity and (parent is not None and parent.is_column_attribute()):
        #     raise errors.InvalidKeyError("column attribute does not accept 'model' key")

        if self.__model_key in entity:
            class_path = entity[self.__model_key]
            return self._class_registry.register_class(class_path)

        # parent is not None
        return referenced_class(get_instrumented_attribute(parent.instance, parent.attr))

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
            self._pre_seed(
                entity=value, parent=EntityTuple(instance, attr_name))

    def _setup_instance(self, class_, kwargs: dict, key, parent: EntityTuple):
        filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix)

        if key == key.data():
            instance = self._setup_data_instance(
                class_, filtered_kwargs, parent)
        else:  # key == key.filter()
            # instance = self.session.query(class_).filter_by(**filtered_kwargs)
            instance = self._setup_filter_instance(
                class_, filtered_kwargs, parent
            )

        # setting parent
        if parent is not None:
            set_instance_attribute(parent.instance, parent.attr, instance)

        return instance

    def _setup_data_instance(self, class_, filtered_kwargs, parent: EntityTuple):
        if parent is not None and attr_is_column(get_instrumented_attribute(parent.instance, parent.attr)):
            raise errors.InvalidKeyError(
                "'data' key is invalid for a column attribute.")

        instance = class_(**filtered_kwargs)

        if parent is None:
            self.session.add(instance)
            self._instances.append(instance)

        return instance

    def _setup_filter_instance(self, class_, filtered_kwargs, parent: EntityTuple):
        if parent is not None:
            instr_attr = get_instrumented_attribute(
                parent.instance, parent.attr)
        else:
            instr_attr = None

        if instr_attr is not None and attr_is_column(instr_attr):
            column = foreign_key_column(instr_attr)
            return self.session.query(column).filter_by(**filtered_kwargs).one()[0]

        if instr_attr is not None and attr_is_relationship(instr_attr):
            return self.session.query(referenced_class(instr_attr)).filter_by(
                **filtered_kwargs
            ).one()

        return self.session.query(class_).filter_by(**filtered_kwargs).one()
