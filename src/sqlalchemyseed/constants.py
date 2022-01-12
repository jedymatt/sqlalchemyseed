from typing import Any
from sqlalchemyseed.json import JsonKey


MODEL_KEY = JsonKey(key='model', type_=str)
DATA_KEY = JsonKey(key='data', type_=Any)
FILTER_KEY = JsonKey(key='filter', type_=str)
