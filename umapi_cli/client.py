import os
import umapi_client

IMS_HOST = os.environ.get('UMAPI_CLI_IMS_HOST') or 'ims-na1.adobelogin.com'
IMS_JWT = os.environ.get('UMAPI_CLI_IMS_JWT') or '/ims/exchange/jwt/'
UMAPI_URL = os.environ.get('UMAPI_CLI_URL') or 'https://usermanagement.adobe.io/v2/usermanagement'


def create(auth_config, test_mode):
    return umapi_client.Connection(auth_config['org_id'], auth_dict=auth_config, ims_host=IMS_HOST,
                                   ims_endpoint_jwt=IMS_JWT, user_management_endpoint=UMAPI_URL, test_mode=test_mode)
