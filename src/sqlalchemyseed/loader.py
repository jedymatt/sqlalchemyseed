"""
MIT License

Copyright (c) 2021 Jedy Matt Tabasco

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import csv
import json
import sys

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    pass


def load_entities_from_json(json_filepath):
    try:
        with open(json_filepath, 'r') as f:
            entities = json.loads(f.read())
    except FileNotFoundError as error:
        raise FileNotFoundError(error)

    return entities


def load_entities_from_yaml(yaml_filepath):
    if 'yaml' not in sys.modules:
        raise ModuleNotFoundError(
            'PyYAML is not installed and is required to run this function. '
            'To use this function, py -m pip install "sqlalchemyseed[yaml]"'
        )

    try:
        with open(yaml_filepath, 'r') as f:
            entities = yaml.load(f.read(), Loader=yaml.SafeLoader)
    except FileNotFoundError as error:
        raise FileNotFoundError(error)

    return entities


def load_entities_from_csv(csv_filepath: str, model) -> dict:
    """Load entities from csv file

    :param csv_filepath: string csv file path
    :param model: either str or class
    :return: dict of entities
    """
    with open(csv_filepath, 'r') as f:
        source_data = list(map(dict, csv.DictReader(f, skipinitialspace=True)))
        if isinstance(model, str):
            model_name = model
        else:
            model_name = '.'.join([model.__module__, model.__name__])

        entities = {'model': model_name, 'data': source_data}

    return entities
