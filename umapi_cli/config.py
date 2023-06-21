# Copyright 2023 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

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
