# Copyright 2023 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import json as _json
import csv as _csv
from schema import Schema, And, Use, Or


def pretty(fh, record_type):
    return PrettyFormatter(fh, record_type)


def json(fh, record_type):
    return JSONFormatter(fh, record_type)


def csv(fh, record_type):
    return CSVFormatter(fh, record_type)


def _split_groups(v):
    return v.split(',') if len(v) else []


def _join_groups(v):
    return ','.join(v)


class InputHandler:
    """Validate and transform input"""

    formats = {
        'user_create_bulk': Schema({
            "type": And(str, lambda s: s in ('adobeID', 'federatedID', 'enterpriseID')),
            "email": And(str, len),
            "firstname": Or(None, str),
            "lastname": Or(None, str),
            "country": Or(None, And(str, lambda s: len(s) == 2)),
            "username": Or(None, str),
            "domain": Or(None, str),
            "groups": Or(None, list, Use(_split_groups)),
        }),
        'user_delete_bulk': Schema({
            "email": And(str, len),
            "hard_delete": And(str, Use(str.strip), Use(str.lower),
                               lambda s: s in ('y', 'n'), error="hard_delete must be Y or N")
        }),
        'user_update_bulk': Schema({
            "email": And(str, len),
            "email_new": Or(None, str),
            "firstname": Or(None, str),
            "lastname": Or(None, str),
            "username": Or(None, str),
            "add_groups": Or(None, list, Use(_split_groups)),
            "remove_groups": Or(None, list, Use(_split_groups)),
        }),
        'group_create_bulk': Schema({
            "name": And(str, len),
            "description": Or(None, str),
        }),
        'group_update_bulk': Schema({
            "name": And(str, len),
            "name_new": Or(None, str),
            "description": Or(None, str),
            "add_users": Or(None, list, Use(_split_groups)),
            "remove_users": Or(None, list, Use(_split_groups)),
            "add_profiles": Or(None, list, Use(_split_groups)),
            "remove_profiles": Or(None, list, Use(_split_groups)),
        }),
        'group_delete_bulk': Schema({
            "name": And(str, len),
        }),
    }

    def __init__(self, fmt):
        assert fmt in self.formats, "Invalid format"
        self.format = fmt

    def handle(self, rec):
        return self.formats[self.format].validate(rec)


class OutputHandler:
    """Transform output and prepare for formatting"""

    formats = {
        'user_read': [
            "type",
            "email",
            "firstname",
            "lastname",
            "country",
            "username",
            "domain",
            "groups",
        ],
        'group_read': [
            'groupName',
            'type',
            'adminGroupName',
            'memberCount',
            'productName',
            'licenseQuota',
        ],
    }

    def __init__(self, fmt):
        assert fmt in self.formats, "Invalid format"
        self.format = fmt

    def handle(self, record):
        return {k: v for k, v in record.items() if k in self.formats[self.format]}


class PassthroughHandler:
    """Don't validate or transform. Used for error reporting"""

    def __init__(self, _=None):
        pass

    def handle(self, record):
        return record

class Formatter:
    def __init__(self, fh, handler):
        self.records = []
        self.fh = fh
        self.handler = handler

    def record(self, record):
        self.records.append(record)

    def write(self):
        pass

    def read(self):
        pass


class PrettyFormatter(Formatter):
    def write(self):
        for record in (self.handler.handle(r) for r in self.records):
            formatted = []
            padding = max(map(len, record.keys())) + 1
            for k, v in record.items():
                formatted.append("{0:{1}}: {2}".format(k, padding, v))
            formatted.append('\n')
            self.fh.write('\n'.join(formatted))

    def read(self):
        raise NotImplementedError


class JSONFormatter(Formatter):
    def write(self):
        for record in (self.handler.handle(r) for r in self.records):
            _json.dump(record, self.fh)
            self.fh.write('\n')

    def read(self):
        for raw_record in self.fh:
            self.record(self.handler.handle(_json.loads(raw_record)))
        return self.records


class CSVFormatter(Formatter):
    def write(self):
        if not self.records:
            return
        writer = _csv.DictWriter(self.fh, self.fieldnames(self.records), lineterminator='\n')
        writer.writeheader()
        writer.writerows(map(self.format_rec, self.records))

    def read(self):
        reader = _csv.DictReader(self.fh)
        for record in reader:
            self.record(self.handler.handle(record))
        return self.records

    def fieldnames(self, records):
        fieldnames = set()
        for rec in (self.handler.handle(r) for r in records):
            fieldnames.update(set(rec.keys()))
        return sorted(list(fieldnames))

    def format_rec(self, record):
        formatted = {}
        formatted.update(record)
        for k, v in record.items():
            if isinstance(v, list):
                formatted[k] = ','.join(v)
            else:
                formatted[k] = v
        return self.handler.handle(formatted)


def normalize(string):
    return string.lower().strip()
