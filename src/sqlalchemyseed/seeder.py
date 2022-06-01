"""
Seeder module
"""

from typing import Union

import sqlalchemy
from sqlalchemy.orm import Session

from sqlalchemyseed import util


class Seeder:
    """
    Seeder class
    """

    def __init__(self, session: Session) -> None:
        self.session = session

        self._instances = []

    def reset(self):
        """
        Reset seeder.
        """
        self._instances = []

    def seed(self, data: Union[dict, list]) -> None:
        """
        Seed data into database.
        """
        self.reset()

        if isinstance(data, dict):
            self._seed_dict(data)
        elif isinstance(data, list):
            self._seed_list(data)
        else:
            raise TypeError("'data' should be 'dict' or 'list'.")

    @property
    def instances(self) -> list:
        """
        Instances that are created by seeding.

        Returns:
            list: Instances that are created by seeding.
        """
        return self._instances

    def commit(self):
        """
        Commit seeding data into database.
        """
        self.session.commit()

    def _seed_dict(self, data: dict):
        model: str = data.get('model')
        data_: Union[dict, list] = data.get('data')
        where: Union[dict, list] = data.get('where')

        model_class = util.get_model_class(model)

        instances = []
        if where is not None:
            instances = self._seed_where(model_class, where)
        else:  # where is None and data is not None
            instances = self._seed_data_(model_class, data_)

        self._instances.extend(instances)

    def _seed_list(self, data: list):
        for item in data:
            self._seed_dict(item)

    def _seed_dict_where(self, model_class: sqlalchemy.orm.mapper, where: dict):
        kwargs = where.copy()
        kwargs.pop('$rel', None)
        return self.session.query(model_class).filter_by(**kwargs).first()

    def _instantiate_model_class(self, model_class: sqlalchemy.orm.mapper, data_: dict):
        kwargs = data_.copy()
        kwargs.pop('$rel', None)
        return model_class(**kwargs)

    def _seed_rel(self, rel: dict, instance: sqlalchemy.orm.mapper):
        for key, value in rel.items():
            setattr(instance, key, value)

    def _seed_where(self, model_class: sqlalchemy.orm.mapper, where: dict):
        instances = []

        if isinstance(where, dict):
            instance = self._seed_dict_where(model_class, where)
            instances.append(instance)

            self.session.add(instance)

            if where.get('$rel') is not None:
                self._seed_rel(where['$rel'], instance)
        else:
            for item in where:
                instance = self._seed_dict_where(model_class, item)
                instances.append(instance)

                self.session.add_all(instances)

                if item.get('$rel') is not None:
                    self._seed_rel(item['$rel'], instance)

        return instances

    def _seed_data_(self, model_class: sqlalchemy.orm.mapper, data_: dict) -> list:
        instances = []

        if isinstance(data_, dict):
            instance = self._instantiate_model_class(model_class, data_)
            instances.append(instance)

            self.session.add(instance)

            if data_.get('$rel') is not None:
                self._seed_rel(data_['$rel'], instance)
        else:
            for item in data_:
                instance = self._instantiate_model_class(model_class, item)
                instances.append(instance)

                self.session.add_all(instances)

                if item.get('$rel') is not None:
                    self._seed_rel(item['$rel'], instance)

        return instances
