import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import HybridSeeder
from tests.models import Base

engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


class TestHybridSeeder(unittest.TestCase):
    def test_seed(self):
        instance = [
            {
                'model': 'tests.models.Employee',
                'data': [
                    {'name': 'John Smith'},
                    {'name': 'Juan Dela Cruz'}
                ]
            },
            {
                'model': 'tests.models.Company',
                'data': {
                    'name': 'MyCompany',
                    '!employees': {
                        'model': 'tests.models.Employee',
                        'filter': [
                            {
                                'name': 'John Smith'
                            },
                            {
                                'name': 'Juan Dela Cruz'
                            }
                        ]
                    }
                }
            }]

        with Session() as session:
            seeder = HybridSeeder(session)
            seeder.seed(instance)
            self.assertEqual(len(seeder.instances), 3)


if __name__ == '__main__':
    unittest.main()
