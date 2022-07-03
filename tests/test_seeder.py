from logging import Logger, log
import logging
import unittest
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Person

from sqlalchemyseed import Seeder


class TestSeeder(unittest.TestCase):
    """
    TestSeeder
    """

    def setUp(self) -> None:
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(  # pylint: disable=invalid-name
            bind=self.engine,
        )
        self.session = Session()
        self.seeder = Seeder(self.session)
        self.base = Base

    def tearDown(self) -> None:
        self.base.metadata.drop_all(self.engine)
        self.base = None

    def test_valid_with_relationship(self):
        """
        Test valid with relationship
        """
        self.base.metadata.create_all(self.engine)

        self.assertIsNone(self.seeder.seed(
            {
                "model": "tests.models.Person",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": 18,
                    "$rel": {
                        "location": {
                            "data": {
                                "name": "Manila"
                            }
                        }
                    }
                }
            }
        ))

        self.assertEqual(self.seeder.instances[0].name, "Juan Dela Cruz")
        self.assertEqual(self.seeder.instances[0].age, 18)

        self.assertEqual(len(self.seeder.instances), 1)
        self.assertEqual(len(self.session.new), 2)

        self.assertEqual(self.seeder.instances[0], list(self.session.new)[0])
        self.assertEqual(
            self.seeder.instances[0].location, list(self.session.new)[1])

        self.session.expunge_all()

        self.assertIsNone(self.seeder.seed(
            [
                {
                    "model": "tests.models.Location",
                    "data": {
                        "name": "Manila"
                    }
                },
                {
                    "model": "tests.models.Person",
                    "data": {
                        "name": "Juan Dela Cruz",
                        "age": 18,
                        "$rel": {
                            "location": {
                                "where": {
                                    "name": "Manila"
                                }
                            }
                        }
                    }
                }
            ]
        ))

        self.assertEqual(len(self.seeder.instances), 2)
        self.assertEqual(len(self.session.dirty), 2)

        self.assertCountEqual(self.seeder.instances, self.session.dirty)

        self.assertEqual(
            self.seeder.instances[1].location,
            self.seeder.instances[0]
        )

        self.assertEqual(
            self.seeder.instances[0].persons[0],
            self.seeder.instances[1]
        )

        self.assertIsNone(self.seeder.seed(
            {
                "model": "tests.models.Person",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": 18,
                    "$rel": {
                        "location": {
                            "where": {
                                "name": "Manila"
                            }
                        },
                        "spouse": {
                            "data": {
                                "name": "Juana Dela Cruz"
                            }
                        }
                    }
                }
            }
        ))

        self.assertIsNone(self.seeder.seed(
            {
                "model": "tests.models.Person",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": 18,
                    "$rel": {
                        "location": {
                            "model": "tests.models.Location",
                            "where": {
                                "name": "Manila"
                            }
                        }
                    }
                }
            }
        ))

        self.assertIsNone(self.seeder.seed(
            [
                {
                    "model": "tests.models.Car",
                    "data": [
                        {
                            "name": "Toyota",
                        },
                        {
                            "name": "Honda",
                        }
                    ]
                },
                {
                    "model": "tests.models.Person",
                    "data": {
                        "name": "Juan Dela Cruz",
                        "age": 18,
                        "$rel": {
                            "cars": [
                                {
                                    "model": "tests.models.Car",
                                    "where": {
                                        "name": "Toyota"
                                    }
                                },
                                {
                                    "model": "tests.models.Car",
                                    "where": {
                                        "name": "Honda"
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        ))

        self.assertIsNone(self.seeder.seed(
            {
                "model": "tests.models.Person",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": 18,
                    "$rel": {
                        "cars": {
                            "model": "tests.models.Car",
                            "where": [
                                {
                                    "name": "Toyota"
                                },
                                {
                                    "name": "Honda"
                                }
                            ]
                        }
                    }
                }
            }
        ))

    def test_valid_data_without_relationship(self):
        """
        Test valid data without relationship
        """
        self.base.metadata.create_all(self.engine)

        self.seeder.seed(
            {
                "model": "tests.models.Person",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": 18
                }
            }
        )

        self.assertEqual(self.seeder.instances[0].name, "Juan Dela Cruz")
        self.assertEqual(self.seeder.instances[0].age, 18)

        self.assertCountEqual(self.seeder.instances, self.session.new)
        self.assertEqual(self.seeder.instances[0], list(self.session.new)[0])

        self.session.expunge_all()

        self.seeder.seed(
            {
                "model": "tests.models.Person",
                "data": [
                    {
                        "name": "Juan Dela Cruz",
                        "age": 18,
                    },
                    {
                        "name": "Juana Dela Cruz",
                    }
                ]
            }
        )

        self.assertEqual(self.seeder.instances[0].name, "Juan Dela Cruz")
        self.assertEqual(self.seeder.instances[0].age, 18)
        self.assertEqual(self.seeder.instances[1].name, "Juana Dela Cruz")
        self.assertEqual(self.seeder.instances[1].age, None)

        self.assertCountEqual(self.seeder.instances, self.session.new)
        self.assertEqual(self.seeder.instances[0], list(self.session.new)[0])
        self.assertEqual(self.seeder.instances[1], list(self.session.new)[1])

        self.session.expunge_all()

        self.assertIsNone(self.seeder.seed(
            [
                {
                    "model": "tests.models.Person",
                    "data": {
                          "name": "Juan Dela Cruz",
                          "age": "18",
                          }
                },
                {
                    "model": "tests.models.Person",
                    "where": {
                        "name": "Juan Dela Cruz",
                        "age": "18",
                    }
                }
            ]
        ))
