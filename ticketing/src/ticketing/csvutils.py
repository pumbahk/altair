import csv
import cStringIO
import codecs

class EncodingTransrator(object):
    def __init__(self, reader, encoding="cp932"):
        self.reader = reader
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        return [s.decode(self.encoding, "utf-8") for s in row]


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    from: http://www.python.jp/doc/release/library/csv.html
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
def reader(csvfile, dialect="excel", encoding="cp932", **kwargs):
    reader = csv.reader(csvfile, dialect=dialect, **kwargs)
    return EncodingTransrator(reader, encoding=encoding)

def writer(csvfile, dialect="excel", encoding="cp932", **kwargs):
    return UnicodeWriter(csvfile, dialect=dialect, encoding=encoding, **kwargs)
