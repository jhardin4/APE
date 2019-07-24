import json
from json import JSONDecodeError


def value_to_str(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    elif isinstance(value, (bool, int, float, str)):
        return str(value)
    else:
        return str(type(value))


def str_to_value(string, old_value=None):
    try:
        return json.loads(string)  # first try to convert from JSON
    except JSONDecodeError:
        pass
    if old_value is None:
        return string
    elif isinstance(old_value, (bool, int, float, str)):
        type_ = type(old_value)
        return type_(string)
    else:
        return None
