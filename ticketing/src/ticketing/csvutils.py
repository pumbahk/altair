import csv

class EncodingTransrator(object):
    def __init__(self, reader, encoding="cp932"):
        self.reader = reader
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        return [s.decode(self.encoding, "utf-8") for s in row]

def reader(csvfile, dialect="excel", encoding="cp932", **kwargs):
    reader = csv.reader(csvfile, dialect=dialect, **kwargs)
    return EncodingTransrator(reader, encoding=encoding)
