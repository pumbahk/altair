from __future__ import absolute_import
import csv
from six import text_type

PREFERRED_MIME_TYPE = 'text/csv'

class CsvTabularDataReader(object):
    preferred_mime_type = PREFERRED_MIME_TYPE

    def __init__(self, exts, names):
        self.exts = exts
        self.names = names

    def open(self, f, encoding='ASCII', dialect='excel', **options):
        if isinstance(f, (str, text_type)):
            f = open(f)
        for cols in csv.reader(f, dialect=dialect, **options):
            yield tuple(text_type(col, encoding) for col in cols)


class CSVWriterWrapper(object):
    def __init__(self, writer, f, encoding, need_close):
        self.writer = writer
        self.f = f
        self.encoding = encoding
        self.need_close = need_close

    def close(self):
        if self.f is not None:
            if self.need_close:
                self.f.close()
        self.f = None

    def __call__(self, cols):
        self.writer.writerow([col.encode(self.encoding) for col in cols]) 


class CsvTabularDataWriter(object):
    preferred_mime_type = PREFERRED_MIME_TYPE

    def __init__(self, exts, names):
        self.exts = exts
        self.names = names

    def open(self, f, encoding='ASCII', dialect='excel', **options):
        if isinstance(f, (str, text_type)):
            f = open(f, 'wb')
            need_close = True
        else:
            need_close = False
        return CSVWriterWrapper(csv.writer(f, dialect=dialect, **options), f, encoding, need_close)
