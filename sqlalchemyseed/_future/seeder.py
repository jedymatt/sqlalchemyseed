from typing import NamedTuple

import sqlalchemy
from sqlalchemy.orm.relationships import RelationshipProperty

from sqlalchemyseed import errors, validator
from sqlalchemyseed import class_registry


class Entity(NamedTuple):
    instance: object
    attr_name: str

    @property
    def cls_attribute(self):
        return getattr(self.instance.__class__, self.attr_name)

    @property
    def ins_attribute(self):
        return getattr(self.instance, self.attr_name)

    @ins_attribute.setter
    def ins_attribute(self, value):
        setattr(self.instance, self.attr_name, value)


# def instantiate_class(class_, filtered_kwargs: dict, key: validator.Key, session: sqlalchemy.orm.Session = None):
#     if key is validator.Key.data():
#         return class_(**filtered_kwargs)
#
#     if key is validator.Key.filter() and session is not None:
#         return session.query(class_).filter_by(**filtered_kwargs).one()


def filter_kwargs(kwargs: dict, class_, ref_prefix):
    return {
        k: v for k, v in kwargs.items()
        if not str(k).startswith(ref_prefix) and not isinstance(getattr(class_, str(k)).property, RelationshipProperty)
    }


def set_parent_attr_value(instance, parent: Entity):
    if isinstance(parent.cls_attribute.property, RelationshipProperty):
        if parent.cls_attribute.property.uselist is True:
            parent.ins_attribute.append(instance)
        else:
            parent.ins_attribute = instance


def iter_ref_attr(attrs, ref_prefix):
    for attr_name, value in attrs.items():
        if str(attr_name).startswith(ref_prefix):
            # remove prefix of attr_name
            yield str(attr_name)[len(ref_prefix):], value


class Seeder:
    __model_key = validator.Key.model()
    __data_key = validator.Key.data()

    def __init__(self, session: sqlalchemy.orm.Session = None, ref_prefix="!"):
        self._session = session
        self._class_registry = class_registry.ClassRegistry()
        self._instances = []
        self.ref_prefix = ref_prefix

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

    # def get_model_class(self, entity, parent: Entity):
    #     model_label = self.__model_key.label
    #     if model_label in entity:
    #         class_path = entity[model_label]
    #         return self._class_registry.register_class(class_path)
    #     # parent is not None
    #     if isinstance(parent.attribute.property, RelationshipProperty):
    #         return parent.attribute.mapper.class_
    #     else:  # parent.attribute is instance of ColumnProperty
    #         table_name = parent.attribute.foreign_keys[0].table.name
    #         class_ = next(
    #             (mapper.class_
    #              for mapper in parent.instance.__class__.registry.mappers
    #              if mapper.class_.__tablename__ == table_name),
    #             errors.ClassNotFoundError(
    #                 "A class with table name '{}' is not found in the mappers".format(table_name)),
    #         )
    #         return class_

    def get_model_class(self, entity, parent: Entity):
        if self.__model_key in entity:
            return self._class_registry.register_class(entity[self.__model_key])
        # parent is not None
        if isinstance(parent.cls_attribute.property, RelationshipProperty):
            return parent.cls_attribute.mapper.class_

    def seed(self, entities, add_to_session=True):
        validator.SchemaValidator.validate(
            entities, ref_prefix=self.ref_prefix)

        self._pre_seed(entities)

        if add_to_session:
            self._session.add_all(self.instances)

    def _pre_seed(self, entity, parent: Entity = None):
        if isinstance(entity, dict):
            self._seed(entity, parent)
        else:  # is list
            for item in entity:
                self._pre_seed(item, parent)

    def _seed(self, entity, parent: Entity = None):
        class_ = self.get_model_class(entity, parent)
        # source_key: validator.Key = next(
        #     (sk for sk in self.__source_keys if sk.label in entity), None)
        # source_data = entity[source_key.label]

        kwargs = entity[self.__data_key]

        if isinstance(kwargs, dict):
            # instantiate object
            instance = self._setup_instance(class_, kwargs, parent)
            for attr_name, value in iter_ref_attr(kwargs, self.ref_prefix):
                self._pre_seed(entity=value, parent=Entity(instance, attr_name))

        else:  # source_data is list
            for kwargs_ in kwargs:
                instance = self._setup_instance(class_, kwargs_, parent)
                for attr_name, value in iter_ref_attr(kwargs_, self.ref_prefix):
                    self._pre_seed(value, parent=Entity(instance, attr_name))

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


class HybridSeeder:
    pass
