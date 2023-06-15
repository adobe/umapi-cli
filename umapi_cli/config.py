import os


keyspec = [{"key": 'UMAPI_CLIENT_ID',     "required": True},
           {"key": 'UMAPI_CLIENT_SECRET', "required": True},
           {"key": 'UMAPI_ORG_ID',        "required": True},
           {"key": 'UMAPI_AUTH_HOST',     "required": False},
           {"key": 'UMAPI_AUTH_ENDPOINT', "required": False},
           {"key": 'UMAPI_URL',           "required": False}]


def get_options():
    options = {}
    for key in keyspec:
        val = os.environ.get(key['key'])
        if key['required'] and val is None:
            raise ValueError(f"Setting '{key['key']}' is required")
        options[key['key']] = val
    return options
