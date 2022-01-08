import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import HybridSeeder, errors
from sqlalchemyseed import Seeder
from tests.models import Base, Company

from tests import instances as ins


# class TestSeeder(unittest.TestCase):
#     """
#     TestSeeder class for testing Seeder class.
#     """
#     def setUp(self) -> None:
#         self.engine = create_engine('sqlite://')
#         Session = sessionmaker(bind=self.engine)
#         session = Session()
#         Base.metadata.create_all(self.engine)
#         self.seeder = Seeder(session)

#     def tearDown(self) -> None:
#         Base.metadata.drop_all(self.engine)
    
#     def test_single(self):
        
class TestSeeder(unittest.TestCase):
    """
    Test class for Seeder class
    """

    def setUp(self) -> None:
        self.engine = create_engine('sqlite://')
        self.Session = sessionmaker(  # pylint: disable=invalid-name
            bind=self.engine,
        )
        self.session = self.Session()
        self.seeder = Seeder(self.session)
        Base.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(self.engine)

    def test_seed_parent(self):
        self.assertIsNone(self.seeder.seed(ins.PARENT))

    def test_seed_parent_add_to_session_false(self):
        self.assertIsNone(self.seeder.seed(ins.PARENT, add_to_session=False))

    def test_seed_parent_with_multi_data(self):
        self.assertIsNone(self.seeder.seed(ins.PARENT_WITH_MULTI_DATA))

    def test_seed_parents(self):
        self.assertIsNone(self.seeder.seed(ins.PARENTS))

    def test_seed_parents_with_empty_data(self):
        self.assertIsNone(self.seeder.seed(ins.PARENTS_WITH_EMPTY_DATA))

    def test_seed_parents_with_multi_data(self):
        self.assertIsNone(self.seeder.seed(ins.PARENTS_WITH_MULTI_DATA))

    def test_seed_parent_to_child(self):
        self.assertIsNone(self.seeder.seed(ins.PARENT_TO_CHILD))

    def test_seed_parent_to_children(self):
        self.assertIsNone(self.seeder.seed(ins.PARENT_TO_CHILDREN))

    def test_seed_parent_to_children_without_model(self):
        self.assertIsNone(self.seeder.seed(
            ins.PARENT_TO_CHILDREN_WITHOUT_MODEL))

    def test_seed_parent_to_children_with_multi_data(self):
        self.assertIsNone(self.seeder.seed(
            ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA))

    def test_seed_parent_to_child_without_child_model(self):
        self.assertIsNone(self.seeder.seed(
            ins.PARENT_TO_CHILD_WITHOUT_CHILD_MODEL))

    def test_seed_parent_to_children_with_multi_data_without_model(self):
        self.assertIsNone(self.seeder.seed(
            ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA_WITHOUT_MODEL))


class TestHybridSeeder(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine('sqlite://')
        self.Session = sessionmaker(
            bind=self.engine)  # pylint: disable=invalid-name
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
                            'filter': {
                                'name': 'MyCompany'
                            }
                        }
                    },
                    {
                        'name': 'Juan Dela Cruz',
                        '!company_id': {
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
            self.assertRaises(errors.InvalidKeyError,
                              lambda: seeder.seed(instance))

    def test_hybrid_seed_parent_to_child_with_ref_attribute(self):
        with self.Session() as session:
            seeder = HybridSeeder(session)
            seeder.seed(ins.HYBRID_SEED_PARENT_TO_CHILD_WITH_REF_COLUMN)
            employee = seeder.instances[1]
            self.assertIsNotNone(employee.company)

    def test_hybrid_seed_parent_to_child_with_ref_attribute_no_model(self):
        with self.Session() as session:
            seeder = HybridSeeder(session)
            self.assertIsNone(seeder.seed(
                ins.HYBRID_SEED_PARENT_TO_CHILD_WITH_REF_COLUMN_NO_MODEL))
            # print(session.new, session.dirty)

    def test_hybrid_seed_parent_to_child_with_ref_attribute_relationship(self):
        with self.Session() as session:
            seeder = HybridSeeder(session)
            self.assertIsNone(seeder.seed(
                ins.HYBRID_SEED_PARENT_TO_CHILD_WITH_REF_RELATIONSHIP))
            # print(session.new, session.dirty)

    def test_hybrid_seed_parent_to_child_with_ref_relationship_no_model(self):
        with self.Session() as session:
            seeder = HybridSeeder(session)
            self.assertIsNone(seeder.seed(
                ins.HYBRID_SEED_PARENT_TO_CHILD_WITH_REF_RELATIONSHIP_NO_MODEL))
            # print(session.new, session.dirty)


class TestSeederCostumizedPrefix(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine('sqlite://')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def test_seeder_parent_to_child(self):
        import json
        custom_instance = json.dumps(ins.PARENT_TO_CHILD)
        custom_instance = custom_instance.replace('!', '@')
        custom_instance = json.loads(custom_instance)

        with self.Session() as session:
            seeder = Seeder(session, ref_prefix='@')
            seeder.seed(custom_instance)
            employee = seeder.instances[0]
            self.assertIsNotNone(employee.company)

    def test_hybrid_seeder_parent_to_child_with_ref_column(self):
        import json
        custom_instance = json.dumps(
            ins.HYBRID_SEED_PARENT_TO_CHILD_WITH_REF_COLUMN)
        custom_instance = custom_instance.replace('!', '@')
        custom_instance = json.loads(custom_instance)

        with self.Session() as session:
            seeder = HybridSeeder(session, ref_prefix='@')
            seeder.seed(custom_instance)
            employee = seeder.instances[1]
            self.assertIsNotNone(employee.company)

    def test_hybrid_seeder_parent_to_child_with_ref_relationship(self):
        import json
        custom_instance = json.dumps(
            ins.HYBRID_SEED_PARENT_TO_CHILD_WITH_REF_RELATIONSHIP)
        custom_instance = custom_instance.replace('!', '@')
        custom_instance = json.loads(custom_instance)

        with self.Session() as session:
            seeder = HybridSeeder(session, ref_prefix='@')
            seeder.seed(custom_instance)
            employee = seeder.instances[1]
            self.assertIsNotNone(employee.company)
