"""
Text file loader module
"""

import csv
import json
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    pass


def load_entities_from_json(json_filepath) -> dict:
    """
    Get entities from json
    """
    try:
        with open(json_filepath, 'r', encoding='utf-8') as file:
            entities = json.loads(file.read())
    except FileNotFoundError as error:
        raise FileNotFoundError from error

    return entities


def load_entities_from_yaml(yaml_filepath):
    """
    Get entities from yaml
    """
    if 'yaml' not in sys.modules:
        raise ModuleNotFoundError(
            'PyYAML is not installed and is required to run this function. '
            'To use this function, py -m pip install "sqlalchemyseed[yaml]"'
        )

    try:
        with open(yaml_filepath, 'r', encoding='utf-8') as file:
            entities = yaml.load(file.read(), Loader=yaml.SafeLoader)
    except FileNotFoundError as error:
        raise FileNotFoundError from error

    return entities


def load_entities_from_csv(csv_filepath: str, model) -> dict:
    """Load entities from csv file

    :param csv_filepath: string csv file path
    :param model: either str or class
    :return: dict of entities
    """
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        source_data = list(
            map(dict, csv.DictReader(file, skipinitialspace=True)))
        if isinstance(model, str):
            model_name = model
        else:
            model_name = '.'.join([model.__module__, model.__name__])

        entities = {'model': model_name, 'data': source_data}

    return entities


_JSON_EXTENSIONS = {".json"}
_YAML_EXTENSIONS = {".yaml", ".yml"}
_CSV_EXTENSIONS = {".csv"}
# Formats that are self-describing (carry their own model) and so can be
# auto-discovered inside a directory. CSV needs an explicit model.
DISCOVERABLE_EXTENSIONS = _JSON_EXTENSIONS | _YAML_EXTENSIONS


def load_path(path, model=None) -> dict:
    """Load entities from a single data file, dispatching on its extension."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in _JSON_EXTENSIONS:
        return load_entities_from_json(str(path))
    if suffix in _YAML_EXTENSIONS:
        return load_entities_from_yaml(str(path))
    if suffix in _CSV_EXTENSIONS:
        return _load_csv(path, model)
    raise ValueError(f"unsupported file type: {path}")


def _load_csv(path, model) -> dict:
    """Load entities from a CSV file, which requires an explicit model."""
    if model is None:
        raise ValueError(f"CSV input requires a model to name the target class: {path}")
    return load_entities_from_csv(str(path), model)
