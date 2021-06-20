import importlib
import json
import os

__version__ = '0.0.1'


def load_entities_from_json(json_filepath):
    if not os.path.exists(json_filepath):
        raise os.error.filename('File does not exist.')

    with open(json_filepath, 'r') as f:
        data = json.loads(f.read())

    return data


def _create_model_objects(session, data):
    objects = []

    for d in data:
        res = _populate_data(session, d)
        objects.append(res)
        session.add(res)
    return objects


def _children_dict_or_list(data):
    for key, value in data.items():
        if isinstance(value, dict) or isinstance(value, list):
            yield key, value


def _populate_data(session, data):
    model = _get_model_class(data['model'])

    if 'data' in data:
        attr = data['data']

        obj = model(**{k: v for k, v in attr.items() if not isinstance(v, dict) and not isinstance(v, list)})
    elif 'filter' in data:
        attr = data['filter']

        obj = session.query(model).filter_by(**attr).one_or_none()
    else:
        raise KeyError('data or filter does not exist.')

    for key, value in _children_dict_or_list(attr):
        if isinstance(value, dict):
            setattr(obj, key, _populate_data(session, value))
        elif isinstance(value, list):
            attrs = [_populate_data(session, i) for i in value]
            setattr(obj, key, attrs)

    return obj


def _get_model_class(model):
    module_name, class_name = str(model).rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def create_objects(session, data):
    return _create_model_objects(session, data)
