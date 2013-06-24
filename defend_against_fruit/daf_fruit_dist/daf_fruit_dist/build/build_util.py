def nested_object_from_json_data(json_data, key, decode_func):
    rv = None
    if key in json_data:
        data = json_data[key]
        if data:
            rv = decode_func(json_data[key])
    return rv


def get_attr_as_tuple_unless_none(object, name):
    value_as_tuple = None
    value = getattr(object, name, None)
    if value is not None:
        value_as_tuple = tuple(value)
    return value_as_tuple


def get_attr_as_list_unless_none(object, name):
    value_as_list = None
    value = getattr(object, name, None)
    if value is not None:
        value_as_list = list(value)
    return value_as_list
