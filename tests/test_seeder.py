import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import HybridSeeder
from sqlalchemyseed import Seeder
from tests.models import Base, Company


class TestSeeder(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine('sqlite://')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)

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

        with self.Session() as session:
            seeder = Seeder(session=session)
            seeder.seed(instance)
            self.assertEqual(len(session.new), 3)

    def test_seed_no_model(self):
        instance = {
            'model': 'tests.models.Company',
            'data': {
                'name': 'MyCompany',
                '!employees': {
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

        with self.Session() as session:
            seeder = Seeder(session=session)
            seeder.seed(instance)
            self.assertEqual(len(session.new), 3)

    def test_seed_multiple_data(self):
        instance = {
            'model': 'tests.models.Company',
            'data': [
                {
                    'name': 'MyCompany',
                    '!employees': {
                        'model': 'tests.models.Employee',
                        'data': {
                            'name': 'John Smith'
                        }

                    }
                },
                {
                    'name': 'MySecondCompany'
                },
            ]
        }

        with self.Session() as session:
            seeder = Seeder(session=session)
            seeder.seed(instance)
            self.assertEqual(len(session.new), 3)

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

        with self.Session() as session:
            seeder = Seeder(session)
            # self.assertIsNone(seeder.seed(instance))
            seeder.seed(instance)
            self.assertEqual(len(session.new), 2)

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

        with self.Session() as session:
            seeder = Seeder(session)
            seeder.seed(instance)
            self.assertEqual(len(session.new), 4)


class TestHybridSeeder(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine('sqlite://')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)

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

        with self.Session() as session:
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

        with self.Session() as session:
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

        with self.Session() as session:
            session.add(
                Company(name='MyCompany')
            )

            seeder = HybridSeeder(session)
            seeder.seed(instance)
            self.assertEqual(len(seeder.instances), 0)

    def test_seed_nested_relationships(self):
        instance = {
            "model": "tests.models.Parent",
            "data": {
                "name": "John Smith",
                "!children": [
                    {
                        "model": "tests.models.Child",
                        "data": {
                            "name": "Mark Smith",
                            "!children": [
                                {
                                    "model": "tests.models.GrandChild",
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

        with self.Session() as session:
            seeder = HybridSeeder(session)
            seeder.seed(instance)
            # print(seeder.instances[0].children[0].children)
            self.assertEqual(
                seeder.instances[0].children[0].children[0].name, "Alice Smith")

    def test_foreign_key_data_instead_of_filter(self):
        instance = {
            'model': 'tests.models.Employee',
            'data': {
                'name': 'John Smith',
                '!company_id': {
                    'model': 'tests.models.Company',
                    'data': {
                        'name': 'MyCompany'
                    }
                }
            },

        }

        with self.Session() as session:
            seeder = HybridSeeder(session)
            self.assertRaises(TypeError, lambda: seeder.seed(instance))


if __name__ == '__main__':
    unittest.main()
