import unittest

from sqlalchemyseed.seeder import ClassRegistry

class TestClassRegistry(unittest.TestCase):
    def test_get_invalid_item(self):
        class_registry = ClassRegistry()
        self.assertRaises(KeyError, lambda: class_registry['InvalidClass'])

    def test_register_class(self):
        cr = ClassRegistry()
        cr.register_class('models.Company')
        from models import Company
        self.assertEqual(cr['models.Company'], Company)
