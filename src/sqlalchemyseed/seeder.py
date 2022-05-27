"""
Seeder module
"""

import abc
from typing import NamedTuple, Union

import sqlalchemy


from . import errors, util, validator
from .attribute import (attr_is_column, attr_is_relationship, foreign_key_column, instrumented_attribute,
                        referenced_class, set_instance_attribute)
from .constants import DATA_KEY, MODEL_KEY, SOURCE_KEYS
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


class InstanceAttributeTuple(NamedTuple):
    """
    Instrance and attribute name tuple
    """
    instance: object
    attr_name: str


def filter_kwargs(kwargs: dict, class_, ref_prefix):
    """
    Filters kwargs
    """
    return {
        k: v for k, v in util.iter_non_ref_kwargs(kwargs, ref_prefix)
        if not attr_is_relationship(instrumented_attribute(class_, str(k)))
    }


class Seeder:
    """
    Basic Seeder class
    """

    def __init__(self, session: sqlalchemy.orm.Session = None, ref_prefix="!"):
        self.session = session
        self.ref_prefix = ref_prefix

        self._instances: list = []
        self._walker: JsonWalker = JsonWalker()
        self._current_parent: InstanceAttributeTuple = None

    @property
    def instances(self) -> tuple:
        """
        Returns instances of the seeded entities
        """
        return tuple(self._instances)

    def _model_class(self):
        """
        Returns class from class path or referenced class
        """
        if MODEL_KEY in self._walker.json:
            class_path = self._walker.json[MODEL_KEY]
            return util.get_model_class(class_path)

        # Expects parent is not None
        instr_attr = getattr(
            self._current_parent.instance.__class__,
            self._current_parent.attr_name
        )
        return referenced_class(instr_attr)

    def seed(self, entities: Union[list, dict], add_to_session=True):
        """
        Seed method
        """
        validator.validate(entities=entities, ref_prefix=self.ref_prefix)

        self._instances.clear()

        self._walker.reset(root=entities)
        self._current_parent = None

        self._pre_seed()

        if add_to_session:
            self.session.add_all(self.instances)

    def _pre_seed(self):
        # iterates current json as list
        # expected json value is [{'model': ...}, ...] or {'model': ...}

        if self._walker.json_is_list:
            for index in range(len(self._walker.json)):
                self._walker.forward([index])
                self._seed()
                self._walker.backward()

        elif self._walker.json_is_dict:
            self._seed()

        self._current_parent = None

    def _seed(self):
        # expected json value is {'model': ..., 'data': ...}
        class_ = self._model_class()

        # moves json.current to json.current[self.__data_key]
        # expected json value is [{'value':...}]
        self._walker.forward([DATA_KEY])
        # iterate json.current as list

        # @lru_cache()
        def init_item():
            kwargs = self._walker.json
            filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix)
            instance = class_(**filtered_kwargs)

            if self._current_parent is not None:
                set_instance_attribute(
                    self._current_parent.instance, self._current_parent.attr_name, instance
                )
            else:
                self._instances.append(instance)

            self._seed_children(instance)

        if self._walker.json_is_list:
            for index in range(len(self._walker.json)):
                self._walker.forward([index])
                init_item()
                self._walker.backward()
        else:
            init_item()

        self._walker.backward()

    def _seed_children(self, instance):
        # expected json is dict:
        # {'model': ...}
        def seed_child():
            key = self._walker.current_key
            if key.startswith(self.ref_prefix):
                attr_name = key[len(self.ref_prefix):]
                self._current_parent = InstanceAttributeTuple(
                    instance, attr_name)
                self._pre_seed()

        self._walker.exec_func_iter(seed_child)


class HybridSeeder(AbstractSeeder):
    """
    HybridSeeder class. Accepts 'filter' key for referencing children.
    """

    def __init__(self, session: sqlalchemy.orm.Session, ref_prefix: str = '!'):
        self.session = session
        self._instances = []
        self.ref_prefix = ref_prefix
        self._walker = JsonWalker()
        self._parent = None

    @property
    def instances(self):
        return tuple(self._instances)

    def get_model_class(self, entity, parent: InstanceAttributeTuple):
        # if self.__model_key in entity and (parent is not None and parent.is_column_attribute()):
        #     raise errors.InvalidKeyError("column attribute does not accept 'model' key")

        if MODEL_KEY in entity:
            class_path = entity[MODEL_KEY]
            return util.get_model_class(class_path)

        # parent is not None
        return referenced_class(instrumented_attribute(parent.instance, parent.attr_name))

    def seed(self, entities):
        validator.hybrid_validate(
            entities=entities, ref_prefix=self.ref_prefix
        )

        self._instances.clear()
        self._walker.reset(root=entities)
        self._parent = None

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
            filter(lambda sk: sk in entity, SOURCE_KEYS)
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
                entity=value, parent=InstanceAttributeTuple(instance, attr_name))

    def _setup_instance(self, class_, kwargs: dict, key: str, parent: InstanceAttributeTuple):
        filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix)

        if key == DATA_KEY:
            instance = self._setup_data_instance(
                class_, filtered_kwargs, parent)
        else:  # key == key.filter()
            # instance = self.session.query(class_).filter_by(**filtered_kwargs)
            instance = self._setup_filter_instance(
                class_, filtered_kwargs, parent
            )

        # setting parent
        if parent is not None:
            set_instance_attribute(parent.instance, parent.attr_name, instance)

        return instance

    def _setup_data_instance(self, class_, filtered_kwargs, parent: InstanceAttributeTuple):
        if parent is not None and attr_is_column(instrumented_attribute(parent.instance, parent.attr_name)):
            raise errors.InvalidKeyError(
                "'data' key is invalid for a column attribute."
            )

        instance = class_(**filtered_kwargs)

        if parent is None:
            self.session.add(instance)
            self._instances.append(instance)

        return instance

    def _setup_filter_instance(self, class_, filtered_kwargs, parent: InstanceAttributeTuple):
        if parent is not None:
            instr_attr = instrumented_attribute(
                parent.instance, parent.attr_name)
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


class DynamicSeeder:
    """
    DynamicSeeder class
    """

    def __init__(self):
        pass
