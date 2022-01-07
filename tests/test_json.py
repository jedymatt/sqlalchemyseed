import unittest
from contextlib import AbstractContextManager
from typing import Any

from sqlalchemyseed.json import JsonWalker
from tests.instances import PARENT, PARENT_TO_CHILD, PARENTS


class TestJsonWalker(unittest.TestCase):
    """
    TestJsonWalker class
    """

    def setUp(self) -> None:
        self.json = JsonWalker()

    def test_parent(self):
        """
        Test parent
        """
        self.json.reset(PARENT)

        def iter_json():
            iter(self.json.iter_as_list())

        self.assertIsNone(iter_json())

    def test_parents(self):
        """
        Test parents
        """
        self.json.reset(PARENTS)

        def iter_json():
            iter(self.json.iter_as_list())

        self.assertIsNone(iter_json())

    def test_parent_to_child(self):
        """
        Test parent to child
        """
        self.json.reset(PARENT_TO_CHILD)

        def iter_json():
            self.json.forward(['data', '!company'])
            iter(self.json.iter_as_list())

        self.assertIsNone(iter_json())


if __name__ == '__main__':
    unittest.main()
