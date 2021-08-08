import unittest

from sqlalchemyseed import load_entities_from_json, load_entities_from_yaml


class TestLoader(unittest.TestCase):
    def test_load_entities_from_json(self):
        entities = load_entities_from_json('tests/res/data.json')

        self.assertEqual(len(entities), 6)

    def test_load_entities_from_yaml(self):
        entities = load_entities_from_yaml('tests/res/data.yml')
        print(entities)
        self.assertEqual(len(entities), 2)
