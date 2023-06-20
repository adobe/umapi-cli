import re
import umapi_client
from umapi_client import UserAction
from .formatter import normalize
from . import log


class ActionQueue:

    def __init__(self, conn):
        self.actions = []
        self.conn = conn

    def push(self, user_action):
        self.actions.append(user_action)

    def execute(self):
        completed = 0
        queued = len(self.actions)
        log.info(f'Number of actions to execute: {len(self.actions)}')
        for action in self.actions:
            _, _, c = self.conn.execute_single(action)
            if c > 0:
                completed += c
                log.info(f"Completion: {completed}/{queued} ({round(completed/queued*100, 2)}%)")
        _, _, c = self.conn.execute_queued()

    def errors(self):
        return [a.execution_errors() for a in self.actions if a.execution_errors()]

    def queue_user_create_action(self, id_type, email, country, firstname=None,
                                 lastname=None, username=None, domain=None, groups=None):
        if username is None or len(username) == 0:
            username = email

        user = UserAction(username, domain)

        user.create(email, firstname, lastname, country, id_type)
        if groups is not None:
            user.add_to_groups(groups)
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
