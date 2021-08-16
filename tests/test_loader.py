import unittest

from sqlalchemyseed import load_entities_from_json
from sqlalchemyseed import load_entities_from_yaml
from sqlalchemyseed import load_entities_from_csv


class TestLoader(unittest.TestCase):
    def test_load_entities_from_json(self):
        entities = load_entities_from_json('tests/res/data.json')
        self.assertEqual(len(entities), 6)

    def test_load_entities_from_yaml(self):
        entities = load_entities_from_yaml('tests/res/data.yml')
        self.assertEqual(len(entities), 2)

    def test_load_entities_from_csv(self):
        entities = load_entities_from_csv('tests/res/companies.csv', 'tests.models.Company')
        self.assertEqual(len(entities['data']), 3)
