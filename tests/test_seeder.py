import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed.seeder import ClassRegistry, HybridSeeder, Seeder
from tests.models import Base

engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


class TestClassRegistry(unittest.TestCase):
    def test_get_invalid_item(self):
        class_registry = ClassRegistry()
        self.assertRaises(KeyError, lambda: class_registry['InvalidClass'])

    def test_register_class(self):
        cr = ClassRegistry()
        cr.register_class('tests.models.Company')
        from tests.models import Company
        self.assertIs(cr['tests.models.Company'], Company)


class TestSeeder(unittest.TestCase):
    def test_seed(self):
        instance = {
            'model': 'tests.models.Company',
            'data': {
                'name': 'MyCompany',
                '!employees': {
                    'model': 'tests.models.Employee',
                    'data': [
                        {
                            'name': 'John Smith'
                        },
                        {
                            'name': 'Juan Dela Cruz'
                        }
                    ]
                }
            }
        }

        seeder = Seeder()
        seeder.seed(instance, False)
        self.assertEqual(len(seeder.instances), 1)

    def test_seed_no_relationship(self):
        instance = {
            'model': 'tests.models.Company',
            'data': [
                {
                    'name': 'Shader',
                },
                {
                    'name': 'One'
                }
            ]
        }

        seeder = Seeder()
        # self.assertIsNone(seeder.seed(instance))
        seeder.seed(instance, False)
        self.assertEqual(len(seeder.instances), 2)

    def test_seed_multiple_entities(self):
        instance = [
            {
                "model": "tests.models.Company",
                "data": {
                    "name": "Mike Corporation",
                    "!employees": {
                        "model": "tests.models.Employee",
                        "data": {
                        }
                    }
                }
            },
            {
                "model": "tests.models.Company",
                "data": [
                    {

                    }
                ]
            },
            {
                "model": "tests.models.Company",
                "data": {

                }
            }
        ]

        seeder = Seeder()
        seeder.seed(instance, False)
        self.assertEqual(len(seeder.instances), 3)


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
