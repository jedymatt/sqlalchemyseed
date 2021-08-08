import json
import sys

try:
    # relative import
    from . import validator
except ImportError:
    import validator


try:
    import yaml
except ModuleNotFoundError:
    pass


def load_entities_from_json(json_filepath):
    try:
        with open(json_filepath, 'r') as f:
            entities = json.loads(f.read())
    except FileNotFoundError as error:
        raise FileNotFoundError(error)

    validator.SchemaValidator.validate(entities)

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

    validator.SchemaValidator.validate(entities)

    return entities


if __name__ == '__main__':
    load_entities_from_yaml('tests/res/data.yaml')
