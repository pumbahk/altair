from os.path import splitext
from pkg_resources import iter_entry_points
from six import text_type

__all__ = [
    'get_reader',
    'lookup_reader',
    'read_tabular_data',
    'get_writer',
    'lookup_writer',
    'read_tabular_data',
    ]

reader_registry = {
    entry_point.name: entry_point
    for entry_point in iter_entry_points(__name__ + '.readers')
    }
readers = {}

writer_registry = {
    entry_point.name: entry_point
    for entry_point in iter_entry_points(__name__ + '.writers')
    }
writers = {}

def get_reader(reader_class):
    reader = readers.get(reader_class)
    if reader is None:
        exts = []
        names = []
        for k, klass in reader_registry.items():
            if klass == reader_class:
                if k[0] == '.':
                    exts.append(k)
                else:
                    names.append(K)
        reader = readers[reader_class] = reader_class(exts=exts, names=names)
    return reader

def get_writer(writer_class):
    writer = writers.get(writer_class)
    if writer is None:
        exts = []
        names = []
        for k, klass in writer_registry.items():
            if klass == writer_class:
                if k[0] == '.':
                    exts.append(k)
                else:
                    names.append(K)
        writer = writers[writer_class] = writer_class(exts=exts, names=names)
    return writer

def _get_file_name(str_or_file_like_object):
    if isinstance(str_or_file_like_object, (str, text_type)):
        return str_or_file_like_object
    else:
        if not hasattr(str_or_file_like_object, 'name'):
            raise TypeError('"type" is neither a string nor a file-like object that has "name" attribute')
        return str_or_file_like_object.name

def lookup_reader(file, type=None):
    if type is None:
        file_name = _get_file_name(file)
        leading, ext = splitext(file_name)
        ext = ext.lower()
        entry_point = reader_registry[ext]
    else:
        entry_point = reader_registry[type]
    reader_class = entry_point.load()
    return get_reader(reader_class)

def lookup_writer(file, type=None):
    if type is None:
        file_name = _get_file_name(file)
        leading, ext = splitext(file_name)
        ext = ext.lower()
        entry_point = writer_registry[ext]
    else:
        entry_point = writer_registry[type]
    writer_class = entry_point.load()
    return get_writer(writer_class)

def read_tabular_data(file, type=None, **options):
    return lookup_reader(file, type).open(file, **options)

def writer_tabular_data(file, type=None, **options):
    return lookup_writer(file, type).open(file, **options)
