import os
import re
import umapi_client

IMS_HOST = os.environ.get('UMAPI_CLI_IMS_HOST') or 'ims-na1.adobelogin.com'
IMS_JWT = os.environ.get('UMAPI_CLI_IMS_JWT') or '/ims/exchange/jwt/'
UMAPI_URL = os.environ.get('UMAPI_CLI_URL') or 'https://usermanagement.adobe.io/v2/usermanagement'
USER_TYPES = {
    'adobeID': umapi_client.IdentityTypes.adobeID,
    'enterpriseID': umapi_client.IdentityTypes.enterpriseID,
    'federatedID': umapi_client.IdentityTypes.federatedID,
}
VALID_COUNTRY = re.compile(r'^[a-zA-Z]{2}$')


def create_conn(auth_config, test_mode):
    return umapi_client.Connection(auth_config['org_id'], auth_dict=auth_config, ims_host=IMS_HOST,
                                   ims_endpoint_jwt=IMS_JWT, user_management_endpoint=UMAPI_URL, test_mode=test_mode)


def user_create_action(user_type, email, username, domain, groups, firstname, lastname, country):
    assert user_type in USER_TYPES, "'{}' is an invalid user type".format(user_type)
    assert VALID_COUNTRY.match(country), "'{}' is an invalid country code format".format(country)
    user = umapi_client.UserAction(USER_TYPES[user_type], email, username, domain)
    user.create(firstname, lastname, country, email)
    if groups is not None:
        user.add_to_groups(groups)
    return user


def user_delete_action(user_type, email, hard_delete=False):
    assert user_type in USER_TYPES, "'{}' is an invalid user type".format(user_type)
    user = umapi_client.UserAction(USER_TYPES[user_type], email)
    user.remove_from_organization(hard_delete)
    return user
