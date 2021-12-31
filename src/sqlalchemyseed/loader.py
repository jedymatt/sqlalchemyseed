"""
Text file loader module
"""

import csv
import json
import sys

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
