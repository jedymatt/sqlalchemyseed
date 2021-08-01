import unittest

from db import session
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import ClassRegistry, Seeder


class TestClassRegistry(unittest.TestCase):
    def test_get_invalid_item(self):
        class_registry = ClassRegistry()
        self.assertRaises(KeyError, lambda: class_registry['InvalidClass'])

    def test_register_class(self):
        cr = ClassRegistry()
        cr.register_class('tests.models.Parent')
        from tests.models import Parent
        self.assertEqual(cr['tests.models.Parent'], Parent)
