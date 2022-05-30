import json
from typing import Union
import sqlalchemy.orm


class Seeder:
    def __init__(self, session: sqlalchemy.orm.Session) -> None:
        self.session = session

        self._instances = []

        self._path = []

    def reset(self):
        self._instances = []
        self._path = []

    def seed(self, data: Union[dict, list]) -> None:
        if isinstance(data, dict):
            self._seed_dict(data)
        elif isinstance(data, list):
            self._seed_list(data)
        else:
            raise TypeError("'data' should be 'dict' or 'list'.")

    def _seed_dict(self, data: dict):
        self._path.append(data)

        self._path.pop()

    def _seed_list(self, data: list):
        self._path.append(data)

        self._path.pop()


engine = sqlalchemy.create_engine('sqlite:///:memory:')
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()

seeder = Seeder(session)

seeder.seed(
    [
        {
            'model': 'User',
            'data': {
                'name': 'John Doe',
                'email': 'johndoe@email.com',
            }
        },
        {
            'model': 'User',
            'data': {
                'name': 'Jane Doe',
                'email': 'johndoe@email.com',
            }
        },
    ]
)
