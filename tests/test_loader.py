import unittest

import pytest

from sqlalchemyseed import loader

from src.sqlalchemyseed import load_entities_from_json
from src.sqlalchemyseed import load_entities_from_yaml
from src.sqlalchemyseed import load_entities_from_csv


def test_load_path_reads_json(tmp_path):
    data_file = tmp_path / "d.json"
    data_file.write_text('{"model": "m.M", "data": []}', encoding="utf-8")
    assert loader.load_path(data_file) == {"model": "m.M", "data": []}


def test_load_path_rejects_unknown_extension(tmp_path):
    bad = tmp_path / "d.txt"
    bad.write_text("nope", encoding="utf-8")
    with pytest.raises(ValueError):
        loader.load_path(bad)


def test_load_path_csv_requires_model(tmp_path):
    csv_file = tmp_path / "d.csv"
    csv_file.write_text("name\nAlice\n", encoding="utf-8")
    with pytest.raises(ValueError):
        loader.load_path(csv_file)


def test_discoverable_extensions_are_json_and_yaml():
    assert loader.DISCOVERABLE_EXTENSIONS == {".json", ".yaml", ".yml"}


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
        yaml_module = loader.sys.modules.pop('yaml')
        try:
            self.assertRaises(
                ModuleNotFoundError,
                lambda: load_entities_from_yaml('tests/res/data.yml')
            )
        finally:
            loader.sys.modules['yaml'] = yaml_module
        
