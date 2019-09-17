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


class PrettyFormatter(Formatter):
    def write(self):
        for record in self.records:
            formatted = []
            padding = max(map(len, record.keys())) + 1
            for k, v in record.items():
                formatted.append("{0:{1}}: {2}".format(k, padding, v))
            formatted.append('\n')
            self.handler.write('\n'.join(formatted))


class JSONFormatter(Formatter):
    def write(self):
        for record in self.records:
            _json.dump(record, self.handler)
            self.handler.write('\n')


class CSVFormatter(Formatter):
    def write(self):
        if not self.records:
            return
        fieldnames = self.records[0].keys()
        writer = _csv.DictWriter(self.handler, fieldnames)
        writer.writeheader()
        writer.writerows(map(self.format_rec, self.records))

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
