import json as _json
import csv as _csv


def pretty(handler):
    return PrettyFormatter(handler)


def json(handler):
    return JSONFormatter(handler)


def csv(handler):
    return CSVFormatter(handler)


class Formatter:
    def __init__(self, handler):
        self.records = []
        self.handler = handler

    def record(self, record):
        self.records.append(record)

    def write(self):
        pass

    def read(self):
        pass


class PrettyFormatter(Formatter):
    def write(self):
        for record in self.records:
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
        for record in self.records:
            _json.dump(record, self.handler)
            self.handler.write('\n')

    def read(self):
        for raw_record in self.handler:
            self.record(_json.loads(raw_record))
        return self.records


class CSVFormatter(Formatter):
    def write(self):
        if not self.records:
            return
        writer = _csv.DictWriter(self.handler, self.fieldnames(self.records), lineterminator='\n')
        writer.writeheader()
        writer.writerows(map(self.format_rec, self.records))

    def read(self):
        reader = _csv.DictReader(self.handler)
        for record in reader:
            self.record({k: self.parse_field(v) for k, v in record.items()})
        return self.records

    @staticmethod
    def fieldnames(records):
        fieldnames = set()
        for rec in records:
            fieldnames.update(set(rec.keys()))
        return sorted(list(fieldnames))

    @staticmethod
    def format_rec(record):
        formatted = {}
        formatted.update(record)
        for k, v in record.items():
            if isinstance(v, list):
                formatted[k] = ','.join(v)
            else:
                formatted[k] = v
        return formatted

    @staticmethod
    def parse_field(field_val):
        return field_val.split(',') if ',' in field_val else field_val
