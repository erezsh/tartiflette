from functools import partial
from tartiflette.executors.field_executors.field_executors import FieldExecutor
from tartiflette.types.helpers import reduce_type


# TODO This could be factorized at schema time


def _object_coerser(_value) -> dict:
    return {}


_COERSER = {"String": str, "Integer": int, "Float": float, "Boolean": bool}


def _list_coerser(func, val) -> list:
    if isinstance(val, list):
        return [func(v) for v in val]
    return [func(val)]


def _not_null_coerser(func, val):
    if not val:
        raise Exception("Shouldn't be null")

    return func(val)


def _get_coerser(field_type):
    rtype = reduce_type(field_type)
    coerser = _object_coerser
    try:
        coerser = _COERSER[rtype]
    except (TypeError, KeyError):
        pass

    try:
        if field_type.is_enum_value:
            coerser = str
    except AttributeError:
        pass

    try:
        if field_type.is_not_null:
            coerser = partial(_not_null_coerser, coerser)
    except AttributeError:
        pass

    try:
        if field_type.is_list:
            coerser = partial(_list_coerser, coerser)
    except AttributeError:
        pass

    return coerser


def get_field_executor(field) -> FieldExecutor:
    return FieldExecutor(field.resolver, _get_coerser(field.gql_type), field)


__all__ = ["get_field_executor", "FieldExecutor"]
