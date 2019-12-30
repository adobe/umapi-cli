import re
import umapi_client
from .formatter import normalize


class ActionQueue:
    USER_TYPES = {
        'adobeID': umapi_client.IdentityTypes.adobeID,
        'enterpriseID': umapi_client.IdentityTypes.enterpriseID,
        'federatedID': umapi_client.IdentityTypes.federatedID,
    }
    VALID_COUNTRY = re.compile(r'^[a-zA-Z]{2}$')

    def __init__(self, conn):
        self.actions = []
        self.conn = conn

    def push(self, user_action):
        self.actions.append(user_action)

    def execute(self):
        for action in self.actions:
            self.conn.execute_single(action)
        self.conn.execute_queued()

    def errors(self):
        return [a.execution_errors() for a in self.actions if a.execution_errors()]

    def queue_user_action(self, user_type, email, username, domain, groups, firstname, lastname, country):
        assert user_type in self.USER_TYPES, "'{}' is an invalid user type".format(user_type)
        assert self.VALID_COUNTRY.match(country), "'{}' is an invalid country code format".format(country)

        update_username = None
        if (user_type == 'federatedID' and username is not None and '@' in username and normalize(email) !=
                normalize(username)):
            update_username = username
            username = email

        user = umapi_client.UserAction(self.USER_TYPES[user_type], email, username, domain)
        user.create(firstname, lastname, country, email)
        if groups is not None:
            user.add_to_groups(groups)
        if update_username:
            user.update(email, update_username)
        self.push(user)

    def queue_delete_action(self, user_type, email, hard_delete=False):
        assert user_type in self.USER_TYPES, "'{}' is an invalid user type".format(user_type)
        user = umapi_client.UserAction(self.USER_TYPES[user_type], email)
        user.remove_from_organization(hard_delete)
        self.push(user)

    def queue_update_action(self, user_type, email, email_new, firstname, lastname, username, country):
        assert user_type in self.USER_TYPES, "'{}' is an invalid user type".format(user_type)
        if not email_new:
            email_new = email
        if email_new == username:
            username = None
        user = umapi_client.UserAction(self.USER_TYPES[user_type], email)
        user.update(email_new, username, firstname, lastname, country)
        self.push(user)
