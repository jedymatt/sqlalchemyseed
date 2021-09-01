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

import abc
from typing import NamedTuple

import sqlalchemy
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql import schema

from . import class_registry, validator, errors, util


class AbstractSeeder(abc.ABC):

    @property
    @abc.abstractmethod
    def instances(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def seed(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _pre_seed(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _seed(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _seed_children(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _setup_instance(self, *args, **kwargs):
        pass


class EntityTuple(NamedTuple):
    instance: object
    attr_name: str


class Entity(EntityTuple):
    @property
    def class_attribute(self):
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
    __model_key = validator.Key.model()
    __data_key = validator.Key.data()

    def __init__(self, session: sqlalchemy.orm.Session = None, ref_prefix="!"):
        self.session = session
        self._class_registry = class_registry.ClassRegistry()
        self._instances = []
        self.ref_prefix = ref_prefix

    @property
    def instances(self):
        return tuple(self._instances)

    def get_model_class(self, entity, parent: Entity):
        if self.__model_key in entity:
            return self._class_registry.register_class(entity[self.__model_key])
        # parent is not None
        return parent.referenced_class

    def seed(self, entities, add_to_session=True):
        validator.validate(entities=entities, ref_prefix=self.ref_prefix)

        self._instances.clear()
        self._class_registry.clear()

        self._pre_seed(entities)

        if add_to_session:
            self.session.add_all(self.instances)

    def _pre_seed(self, entity, parent: Entity = None):
        if isinstance(entity, dict):
            self._seed(entity, parent)
        else:  # is list
            for item in entity:
                self._pre_seed(item, parent)

    def _seed(self, entity, parent: Entity = None):
        class_ = self.get_model_class(entity, parent)

        kwargs = entity[self.__data_key]

        # kwargs is list
        if isinstance(kwargs, list):
            for kwargs_ in kwargs:
                instance = self._setup_instance(class_, kwargs_, parent)
                self._seed_children(instance, kwargs_)
            return

        # kwargs is dict
        # instantiate object
        instance = self._setup_instance(class_, kwargs, parent)
        self._seed_children(instance, kwargs)

    def _seed_children(self, instance, kwargs):
        for attr_name, value in util.iter_ref_kwargs(kwargs, self.ref_prefix):
            self._pre_seed(entity=value, parent=Entity(instance, attr_name))

    def _setup_instance(self, class_, kwargs: dict, parent: Entity):
        instance = class_(**filter_kwargs(kwargs, class_, self.ref_prefix))
        if parent is not None:
            set_parent_attr_value(instance, parent)
        else:
            self._instances.append(instance)
        return instance

    # def instantiate_class(self, class_, kwargs: dict, key: validator.Key):
    #     filtered_kwargs = {
    #         k: v
    #         for k, v in kwargs.items()
    #         if not k.startswith("!")
    #            and not isinstance(getattr(class_, k), RelationshipProperty)
    #     }
    #
    #     if key is validator.Key.data():
    #         return class_(**filtered_kwargs)
    #
    #     if key is validator.Key.filter() and self.session is not None:
    #         return self.session.query(class_).filter_by(**filtered_kwargs).one()


class HybridSeeder(AbstractSeeder):
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
        validator.hybrid_validate(entities=entities, ref_prefix=self.ref_prefix)

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
        instance = self._setup_instance(class_, source_data, source_key, parent)
        self._seed_children(instance, source_data)

    def _seed_children(self, instance, kwargs):
        for attr_name, value in util.iter_ref_kwargs(kwargs, self.ref_prefix):
            self._pre_seed(entity=value, parent=Entity(instance, attr_name))

    def _setup_instance(self, class_, kwargs: dict, key, parent):
        filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix)

        if key == key.data():
            instance = self._setup_data_instance(class_, filtered_kwargs, parent)
        else:  # key == key.filter()
            # instance = self.session.query(class_).filter_by(**filtered_kwargs)
            instance = self._setup_filter_instance(class_, filtered_kwargs, parent)

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
