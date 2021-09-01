import unittest
from sqlalchemyseed import loader

from src.sqlalchemyseed import load_entities_from_json
from src.sqlalchemyseed import load_entities_from_yaml
from src.sqlalchemyseed import load_entities_from_csv

class TestLoader(unittest.TestCase):
    def test_load_entities_from_json(self):
        entities = load_entities_from_json('tests/res/data.json')
        self.assertEqual(len(entities), 6)

    def test_load_entities_from_json_file_not_found(self):
        self.assertRaises(FileNotFoundError,
                          lambda: load_entities_from_json('tests/res/non-existent-file'))

    def test_load_entities_from_yaml(self):
        entities = load_entities_from_yaml('tests/res/data.yml')
        self.assertEqual(len(entities), 2)

    def test_load_entities_from_yaml_file_not_found(self):
        self.assertRaises(FileNotFoundError,
                          lambda: load_entities_from_yaml('tests/res/non-existent-file'))

    def test_load_entities_from_csv_input_class(self):
        from tests.models import Company
        entities = load_entities_from_csv(
            'tests/res/companies.csv', Company)
        self.assertEqual(len(entities['data']), 3)

    def test_load_entities_from_csv_input_model_string(self):
        self.assertIsNotNone(load_entities_from_csv(
            'tests/res/companies.csv', "tests.models.Company"))

    def test_loader_yaml_not_installed(self):
        loader.sys.modules.pop('yaml')
        self.assertRaises(
            ModuleNotFoundError,
            lambda: load_entities_from_yaml('tests/res/data.yml')
        )
        