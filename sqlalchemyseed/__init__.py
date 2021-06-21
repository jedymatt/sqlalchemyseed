import importlib
import json

__version__ = '0.0.2'


class Label:
    MODEL = 'model'
    DATA = 'data'
    FILTER = 'filter'


def load_entities_from_json(json_filepath):
    try:
        with open(json_filepath, 'r') as f:
            data = json.loads(f.read())
    except FileNotFoundError as error:
        raise FileNotFoundError(error)

    return data


def _children_dict_or_list(data):
    for key, value in data.items():
        if isinstance(value, dict) or isinstance(value, list):
            yield key, value


def get_model_instance(model: str):
    try:
        module_name, class_name = model.rsplit('.', 1)
    except ValueError:
        raise ValueError('Invalid module or class input format.')

    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def create_objects(entities, session=None, auto_add=False):
    results = []

    for entity in entities:
        objects = _populate_entity(entity, session)

        if auto_add:
            session.add_all(objects)

        for objects in objects:
            results.append(objects)

    return results


def _populate_entity(entity, session=None):
    if Label.MODEL not in entity:
        raise KeyError("Field 'model' does not exist.")

    model_instance = get_model_instance(entity[Label.MODEL])

    if Label.DATA in entity:
        label = Label.DATA
    elif Label.FILTER in entity:
        label = Label.FILTER
        if session is None:
            raise ValueError("session not found, it is required when using 'filter' field.")
    else:
        raise KeyError("'data' or 'filter' fields does not exist.")

    if not isinstance(entity[label], list):
        group_fields = [entity[label]]
    else:
        group_fields = entity[label]

    objects = []
    for fields in group_fields:
        obj = _populate_fields(fields, model_instance, label, session)

        objects.append(
            obj
        )

    return objects


def _populate_fields(fields, model_instance, label, session=None):
    if label == Label.DATA:
        obj = model_instance(**{k: v for k, v in fields.items() if not isinstance(v, dict) and not isinstance(v, list)})
    elif label == Label.FILTER:
        obj = session.query(model_instance).filter_by(**fields).one_or_none()
    else:
        raise KeyError("'data' or 'filter' fields does not exist.")

    for key, value in _children_dict_or_list(fields):
        if isinstance(value, dict):
            _populate_entity(value, session)
        elif isinstance(value, list):
            attrs = [_populate_entity(entity, session)[0] for entity in value]
            print(key, attrs)
            setattr(obj, key, attrs)

    return obj
