# Copyright 2023 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

from umapi_client import OAuthS2S, Connection


def create_conn(conf, test_mode):
    auth_args = {}
    if conf.get('UMAPI_AUTH_HOST') is not None:
        auth_args['auth_host'] = conf['UMAPI_AUTH_HOST']
    if conf.get('UMAPI_AUTH_ENDPOINT') is not None:
        auth_args['auth_endpoint'] = conf['UMAPI_AUTH_ENDPOINT']

    auth = OAuthS2S(
        client_id=conf['UMAPI_CLIENT_ID'],
        client_secret=conf['UMAPI_CLIENT_SECRET'],
        **auth_args,
    )

    conn_args = {}
    if conf.get('UMAPI_URL') is not None:
        conn_args['endpoint'] = conf['UMAPI_URL']

    return Connection(
        org_id=conf['UMAPI_ORG_ID'],
        auth=auth,
        test_mode=test_mode,
        **conn_args,
    )
