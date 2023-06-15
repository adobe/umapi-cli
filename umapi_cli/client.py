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
