# project/utils.py
from rest_framework.views import exception_handler
from rest_framework.response import Response


def _flatten(value):
    if isinstance(value, list):
        return [str(v) if not isinstance(v, (list, dict)) else str(v) for v in value]
    if isinstance(value, dict):
        # flatten nested serializer errors
        return [f"{k}: {v}" for k, vs in value.items()
                for v in (vs if isinstance(vs, list) else [vs])]
    return [str(value)]

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data

    if isinstance(data, dict) and "detail" in data and len(data) == 1:
        errors = {"detail": _flatten(data["detail"])}
    elif isinstance(data, list):
        errors = {"non_field_errors": _flatten(data)}
    elif isinstance(data, dict):
        errors = {k: _flatten(v) for k, v in data.items()}
    else:
        errors = {"non_field_errors": [str(data)]}

    response.data = {"status": response.status_code, "errors": errors}
    return response