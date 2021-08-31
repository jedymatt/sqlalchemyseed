import unittest
from src.sqlalchemyseed import errors

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

    def test_get_classes(self):
        class_registry = ClassRegistry()
        class_registry.register_class('tests.models.Company')
        self.assertIsNotNone(class_registry.classes)

    def test_register_invalid_string_format(self):
        class_registry = ClassRegistry()
        self.assertRaises(
            errors.ParseError,
            lambda: class_registry.register_class('RandomString')
        )
