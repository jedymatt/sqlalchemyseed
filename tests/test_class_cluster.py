import unittest

from sqlalchemyseed.class_cluster import ClassCluster


class TestClassCluster(unittest.TestCase):
    def test_get_invalid_item(self):
        class_cluster = ClassCluster()
        self.assertRaises(KeyError, lambda: class_cluster['InvalidClass'])

    def test_register_class(self):
        class_cluster = ClassCluster()
        class_cluster.add_class('tests.models.Company')
        from .models import Company
        self.assertIs(class_cluster['tests.models.Company'], Company)
