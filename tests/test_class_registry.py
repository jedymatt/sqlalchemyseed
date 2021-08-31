import unittest

from src.sqlalchemyseed.class_registry import ClassRegistry


class TestClassRegistry(unittest.TestCase):
    def test_get_invalid_item(self):
        class_registry = ClassRegistry()
        self.assertRaises(KeyError, lambda: class_registry['InvalidClass'])

    def test_register_class(self):
        class_registry = ClassRegistry()
        class_registry.register_class('tests.models.Company')
        from tests.models import Company
        self.assertIs(class_registry['tests.models.Company'], Company)
