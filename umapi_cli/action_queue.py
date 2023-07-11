# Copyright 2023 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import re
import umapi_client
from umapi_client import UserAction, GroupAction
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
            self.conn.execute_single(action)
            completed += 1
            if completed % 10 == 0:
                log.info(f"Executed actions: {completed}/{queued} ({round(completed/queued*100, 2)}%)")
        self.conn.execute_queued()
        log.info(f"Executed actions: {completed}/{queued} ({round(completed/queued*100, 2)}%)")
        return completed

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

    def queue_group_create_action(self, name, description):
        group = GroupAction(name)
        group.create(description=description)
        self.push(group)

    def queue_group_update_action(self, name, name_new, description, add_users,
                                  remove_users, add_profiles, remove_profiles):
        group = GroupAction(name)
        if name_new is not None or description is not None:
            group.update(name=name_new, description=description)
        if add_users is not None:
            group.add_users(add_users)
        if remove_users is not None:
            group.remove_users(remove_users)
        if add_profiles:
            group.add_to_products(add_profiles)
        if remove_profiles is not None:
            group.remove_from_products(remove_profiles)
        self.push(group)

    def queue_group_delete_action(self, name):
        # there is a bug in the UMAPI that prevents multiple group delete
        # operations in a single action call
        group = GroupAction(name)
        group.delete()
        self.conn.execute_single(group, immediate=True)

    def queue_delete_action(self, email, hard_delete=False):
        user = UserAction(email)
        user.remove_from_organization(hard_delete)
        self.push(user)

    def queue_update_action(self, email, **kwargs):
        user = UserAction(email)
        params = {}
        groups_to_add = []
        groups_to_remove = []
        for k,v in kwargs.items():
            if k == 'add_groups':
                groups_to_add = v
                continue
            if k == 'remove_groups':
                groups_to_remove = v
                continue
            if k == 'email_new':
                params['email'] = v
                continue
            params[k] = v
        user.update(**params)
        if groups_to_add:
            user.add_to_groups(groups_to_add)
        if groups_to_remove:
            user.remove_from_groups(groups_to_remove)
        self.push(user)
