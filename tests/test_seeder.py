import unittest
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import HybridSeeder, Seeder, errors
from tests import instances as ins
from tests.models import Base, Company
from tests.relationships import association_object, many_to_many, many_to_one, one_to_many, one_to_one


class TestSeederRelationship(unittest.TestCase):
    """
    TestSeederRelationship class for testing Seeder class dealing with relationships.
    """

    def setUp(self) -> None:

        self.engine = create_engine('sqlite://')
        Session = sessionmaker(  # pylint: disable=invalid-name
            bind=self.engine
        )
        session = Session()
        self.seeder = Seeder(session)
        self.base = None

    def tearDown(self) -> None:
        self.base.metadata.drop_all(self.engine)
        self.base = None

    def test_seed_one_to_many(self):
        """
        Test seed one to many relationship
        """

        self.base = one_to_many.Base
        self.base.metadata.create_all(self.engine)

        module_path = 'tests.relationships.one_to_many'

        json = \
            {
                'model': f'{module_path}.Parent',
                'data': {
                    'value': 'parent_1',
                    '!children': [
                        {
                            'model': f'{module_path}.Child',
                            'data': {
                                'value': 'child_1'
                            },
                        },
                        {
                            'model': f'{module_path}.Child',
                            'data': {
                                'value': 'child_2'
                            },
                        },
                    ],
                },
            }
        self.seeder.seed(json)

        # seeder.instances should only contain the first level entities
        self.assertEqual(len(self.seeder.instances), 1)

        # assign classes to remove module
        Parent = one_to_many.Parent
        Child = one_to_many.Child

        parent: Parent = self.seeder.instances[0]
        children: List[Child] = parent.children

        self.assertEqual(parent.value, 'parent_1')
        self.assertEqual(len(children), 2)

        self.assertEqual(children[0].value, 'child_1')
        self.assertEqual(children[0].parent, parent)

        self.assertEqual(children[1].value, 'child_2')
        self.assertEqual(children[1].parent, parent)

    def test_seed_many_to_one(self):
        """
        Test seed many to one relationship
        """

        self.base = many_to_one.Base
        self.base.metadata.create_all(self.engine)

        module_path = 'tests.relationships.many_to_one'

        json = \
            [
                {
                    'model': f'{module_path}.Parent',
                    'data': {
                        'value': 'parent_1',
                        '!child': {
                            'model': f'{module_path}.Child',
                            'data': {
                                'value': 'child_1'
                            }
                        }
                    }
                },
                {
                    'model': f'{module_path}.Parent',
                    'data': {
                        'value': 'parent_2',
                        '!child': {
                            'model': f'{module_path}.Child',
                            'data': {
                                'value': 'child_2'
                            }
                        }
                    }
                }
            ]

        self.seeder.seed(json)

        Parent = many_to_one.Parent

        self.assertEqual(len(self.seeder.instances), 2)

        parents: List[Parent] = self.seeder.instances

        parent_1 = parents[0]
        self.assertEqual(parent_1.value, 'parent_1')
        self.assertEqual(parent_1.child.value, 'child_1')
        self.assertEqual(parent_1.child.parents, [parent_1])

        parent_2 = parents[1]
        self.assertEqual(parent_2.value, 'parent_2')
        self.assertEqual(parent_2.child.value, 'child_2')
        self.assertEqual(parent_2.child.parents, [parent_2])

    def test_seed_one_to_one(self):
        """
        Test seed one to one relationship
        """

        self.base = one_to_one.Base
        self.base.metadata.create_all(self.engine)

        module_path = 'tests.relationships.one_to_one'

        json = \
            {
                'model': f'{module_path}.Parent',
                'data': {
                    'value': 'parent_1',
                    '!child': {
                        'model': f'{module_path}.Child',
                        'data': {
                            'value': 'child_1'
                        }
                    }
                }
            }

        self.seeder.seed(json)

        self.assertEqual(len(self.seeder.instances), 1)

        parent = self.seeder.instances[0]
        child = parent.child

        self.assertEqual(parent.value, 'parent_1')
        self.assertEqual(child.value, 'child_1')

        self.assertEqual(child.parent, parent)

    def test_seed_many_to_many(self):
        """
        Test seed many to many relationship
        """

        self.base = many_to_many.Base
        self.base.metadata.create_all(self.engine)

        module_path = 'tests.relationships.many_to_many'

        json = \
            [
                {
                    'model': f'{module_path}.Parent',
                    'data': {
                        'value': 'parent_1',
                        '!children': [
                            {
                                'model': f'{module_path}.Child',
                                'data': {
                                    'value': 'child_1'
                                }
                            },
                            {
                                'model': f'{module_path}.Child',
                                'data': {
                                    'value': 'child_2'
                                }
                            }
                        ]
                    }
                },
                {
                    'model': f'{module_path}.Parent',
                    'data': {
                        'value': 'parent_2',
                        '!children': [
                            {
                                'model': f'{module_path}.Child',
                                'data': {
                                    'value': 'child_3'
                                }
                            },
                            {
                                'model': f'{module_path}.Child',
                                'data': {
                                    'value': 'child_4'
                                }
                            }
                        ]
                    }
                }
            ]
        self.seeder.seed(json)

        self.assertEqual(len(self.seeder.instances), 2)

        parents = self.seeder.instances

        parents: List[many_to_many.Parent] = self.seeder.instances

        self.assertEqual(len(parents), 2)

        # parent 1
        parent_1: many_to_many.Parent = parents[0]
        self.assertEqual(parent_1.value, 'parent_1')

        parent_1_children: List[many_to_many.Child] = parent_1.children
        self.assertEqual(len(parent_1_children), 2)

        child_1 = parent_1_children[0]
        self.assertEqual(child_1.value, 'child_1')
        self.assertEqual(child_1.parents, [parent_1])

        child_2 = parent_1_children[1]
        self.assertEqual(child_2.value, 'child_2')
        self.assertEqual(child_2.parents, [parent_1])

        # parent 2
        parent_2: many_to_many.Parent = parents[1]
        self.assertEqual(parent_2.value, 'parent_2')

        parent_2_children: List[many_to_many.Child] = parent_2.children
        self.assertEqual(len(parent_2_children), 2)

        child_3 = parent_2_children[0]
        self.assertEqual(child_3.value, 'child_3')
        self.assertEqual(child_3.parents, [parent_2])

        child_4 = parent_2_children[1]
        self.assertEqual(child_4.value, 'child_4')
        self.assertEqual(child_4.parents, [parent_2])

    def test_seed_association_object(self):
        """
        Test seed association object relationship
        """

        self.base = many_to_many.Base
        self.base.metadata.create_all(self.engine)

        module_path = 'tests.relationships.association_object'

        json = \
            {
                'model': f'{module_path}.Parent',
                'data': {
                    'value': 'parent_1',
                    '!children': [
                        {
                            'model': f'{module_path}.Association',
                            'data': {
                                'extra_value': 'association_1',
                                '!child': {
                                    'model': f'{module_path}.Child',
                                    'data': {
                                        'value': 'child_1'
                                    }
                                }
                            }
                        }
                    ]
                }
            }

        self.seeder.seed(json)

        self.assertEqual(len(self.seeder.instances), 1)

        parent: association_object.Parent = self.seeder.instances[0]
        self.assertEqual(parent.value, 'parent_1')

        self.assertEqual(len(parent.children), 1)
        association: association_object.Association = parent.children[0]
        self.assertEqual(association.extra_value, 'association_1')
        self.assertEqual(association.parent, parent)
        self.assertIsNotNone(association.child)

        child: association_object.Child = association.child
        self.assertEqual(child.value, 'child_1')
        self.assertEqual(child.parents[0], association)


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
