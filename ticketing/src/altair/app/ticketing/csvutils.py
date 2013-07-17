import csv
import cStringIO
import codecs
import re
from collections import OrderedDict
from altair.app.ticketing.utils import dereference

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

class SimpleRenderer(object):
    def __init__(self, key, name=None, empty_if_dereference_fails=True):
        self.key = key
        self.name = key if name is None else name
        self.empty_if_dereference_fails = empty_if_dereference_fails

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.key, self.name)

class PlainTextRenderer(SimpleRenderer):
    def __init__(self, key, name=None, empty_if_dereference_fails=True, fancy=False):
        super(PlainTextRenderer, self).__init__(key, name, empty_if_dereference_fails)
        self.fancy = fancy

    def __call__(self, record):
        value = dereference(record, self.key, self.empty_if_dereference_fails)
        return [
            ((u'', self.name, u''), (u'="%s"' % unicode(value) if self.fancy else unicode(value)) if value is not None else u'')
            ]

class CollectionRenderer(object):
    def __init__(self, key, variable_name, renderers):
        self.key = key
        self.variable_name = variable_name 
        self.renderers = renderers

    def __call__(self, record):
        items = dereference(record, self.key)
        retval = []
        for i, item in enumerate(items):
            for renderer in self.renderers:
                for column, rendered in renderer({self.variable_name: item}):
                    retval.append((
                        (column[0], column[1], (u'[%d]' % i) + column[2]),
                        rendered))
        return retval

class AttributeRenderer(object):
    def __init__(self, key, variable_name, renderer_class=PlainTextRenderer):
        #assert isinstance(renderer_class, SimpleRenderer)
        self.key = key
        self.variable_name = variable_name
        self.renderer_class = renderer_class

    def __call__(self, record):
        items = dereference(record, self.key)
        retval = []
        for attr_key, attr_value in items.items():
            renderer = self.renderer_class(u'_[%s]' % attr_key, u'%s[%s]' % (self.variable_name, attr_key))
            retval.extend(renderer(dict(_=items)))
        return retval

class CSVRenderer(object):
    def __init__(self, column_renderers):
        self.column_renderers = column_renderers
        self.column_sets = {}
        self.rows = []

    def append(self, record):
        rendered_dict = {}
        for column_renderer in self.column_renderers:
            rendered = column_renderer(record)
            rendered_dict[column_renderer] = dict(rendered)
            column_set = self.column_sets.get(column_renderer)
            if column_set is None:
                column_set = self.column_sets[column_renderer] = OrderedDict()
            for column, _ in rendered:
                column_set[column] = True

        self.rows.append(rendered_dict)

    def render_header(self, localized_columns={}):
        return [
            column[0] + localized_columns.get(column[1], column[1]) + column[2] \
            for renderer in self.column_renderers \
            for column in self.column_sets.get(renderer, {}).keys()
            ]

    def render_rows(self):
        for row in self.rows:
            yield [
                row[renderer].get(column, u'')
                for renderer in self.column_renderers \
                for column in self.column_sets[renderer].keys()
                ]

    def render(self, localized_columns={}):
        yield self.render_header(localized_columns)
        for row_data in self.render_rows():
            yield row_data

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)

