from __future__ import absolute_import
import csv
from six import text_type

class CsvTabularDataReader(object):
    def __init__(self, exts, names):
        self.exts = exts
        self.names = names

    def open(self, f, encoding='ASCII', dialect='excel', **options):
        if isinstance(f, (str, text_type)):
            f = open(f)
        for cols in csv.reader(f, dialect=dialect, **options):
            yield tuple(text_type(col, encoding) for col in cols)


class CSVWriterWrapper(object):
    def __init__(self, writer, f):
        self.writer = writer
        self.f = f

    def close(self):
        self.f.close()

    def __call__(self, cols):
        self.writer.writerow(cols) 


class CsvTabularDataWriter(object):
    def open(self, f, encoding='ASCII', dialect='excel', **options):
        if isinstance(f, (str, text_type)):
            f = open(f, 'wb')
        return CSVWriterWrapper(csv.writer(f, dialect=dialect, **options), f)
