import json as _json
import csv as _csv


def pretty(handler):
    return PrettyFormatter(handler)


def json(handler):
    return JSONFormatter(handler)


def csv(handler):
    return CSVFormatter(handler)


class Formatter:
    output_format = [
        "country",
        "domain",
        "email",
        "username",
        "firstname",
        "lastname",
        "groups",
        "type",
    ]

    def __init__(self, handler):
        self.records = []
        self.handler = handler

    def record(self, record):
        self.records.append(record)

    @classmethod
    def format_output(cls, record):
        return {k: v for k, v in record.items() if k in cls.output_format}

    def write(self):
        pass

    def read(self):
        pass


class PrettyFormatter(Formatter):
    def write(self):
        for record in (self.format_output(r) for r in self.records):
            formatted = []
            padding = max(map(len, record.keys())) + 1
            for k, v in record.items():
                formatted.append("{0:{1}}: {2}".format(k, padding, v))
            formatted.append('\n')
            self.handler.write('\n'.join(formatted))

    def read(self):
        raise NotImplementedError


class JSONFormatter(Formatter):
    def write(self):
        for record in (self.format_output(r) for r in self.records):
            _json.dump(record, self.handler)
            self.handler.write('\n')

    def read(self):
        for raw_record in self.handler:
            self.record(_json.loads(raw_record))
        return self.records


class CSVFormatter(Formatter):
    split_fields = ['groups']

    def write(self):
        if not self.records:
            return
        writer = _csv.DictWriter(self.handler, self.fieldnames(self.records), lineterminator='\n')
        writer.writeheader()
        writer.writerows(map(self.format_rec, self.records))

    def read(self):
        reader = _csv.DictReader(self.handler)
        for record in reader:
            self.record({k: self.parse_field(k, v) for k, v in record.items()})
        return self.records

    def fieldnames(self, records):
        fieldnames = set()
        for rec in (self.format_output(r) for r in records):
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
        return self.format_output(formatted)

    @classmethod
    def parse_field(cls, field_name, field_val):
        return field_val.split(',') if field_name in cls.split_fields else field_val
