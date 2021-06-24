import json
from types import SimpleNamespace

from jsonschema import Draft7Validator
from jsonschema import ValidationError

SCHEMA_PATH = 'sqlalchemyseed/schema.json'
DATA_PATH = 'tests/object_root.json'

with open(SCHEMA_PATH, 'r') as f:
    data = f.read()

    schema = json.loads(data)
    schema_instance = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

with open(DATA_PATH, 'r') as f:
    entities = json.loads(f.read())

Validator = Draft7Validator

validator = Validator(schema)

try:
    validator.validate(entities)
except ValidationError as error:
    result = Draft7Validator.TYPE_CHECKER.is_type(error.instance, "object")
    print(result)


