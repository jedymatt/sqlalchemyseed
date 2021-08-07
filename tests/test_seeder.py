import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import ClassRegistry, HybridSeeder, Seeder
from tests.models import Base, Company

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

        with Session() as session:
            seeder = Seeder(session=session)
            seeder.seed(instance)
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

        with Session() as session:
            seeder = Seeder(session)
            seeder.seed(instance, False)
            self.assertEqual(len(seeder.instances), 3)


class TestHybridSeeder(unittest.TestCase):
    def test_hybrid_seed_with_relationship(self):
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
            # session.expire_all()

    def test_filter_with_foreign_key(self):
        instance = [
            {
                'model': 'tests.models.Company',
                'data': {
                    'name': 'MyCompany'
                }
            },
            {
                'model': 'tests.models.Employee',
                'data': [
                    {
                        'name': 'John Smith',
                        '!company_id': {
                            'model': 'tests.models.Company',
                            'filter': {
                                'name': 'MyCompany'
                            }
                        }
                    },
                    {
                        'name': 'Juan Dela Cruz',
                        '!company_id': {
                            'model': 'tests.models.Company',
                            'filter': {
                                'name': 'MyCompany'
                            }
                        }
                    }
                ]
            },
        ]

        with Session() as session:
            seeder = HybridSeeder(session)
            seeder.seed(instance)
            self.assertEqual(len(seeder.instances), 3)
            # session.expire_all()

    def test_no_data_key_field(self):
        instance = [
            {
                'model': 'tests.models.Company',
                'filter': {'name': 'MyCompany'}
            }
        ]

        with Session() as session:
            session.add(
                Company(name='MyCompany')
            )

            seeder = HybridSeeder(session)
            seeder.seed(instance)
            self.assertEqual(len(seeder.instances), 0)

    def test_seed_nested_relationships(self):
        instance = {
            "model": "models.Parent",
            "data": {
                "name": "John Smith",
                "!children": [
                    {
                        "model": "models.Child",
                        "data": {
                            "name": "Mark Smith",
                            "!children": [
                                {
                                    "model": "models.GrandChild",
                                    "data": {
                                        "name": "Alice Smith"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        with Session() as session:
            seeder = HybridSeeder(session)
            seeder.seed(instance)
            print(seeder.instances[0].children[0].children)
            self.assertEqual(
                seeder.instances[0].children[0].children[0].name, "Alice Smith")


if __name__ == '__main__':
    unittest.main()
