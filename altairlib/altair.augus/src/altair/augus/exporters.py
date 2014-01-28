#-*- coding: utf-8 -*-
import csv
from . import DEFAULT_ENCODING
class AugusExporter(object):
    @classmethod
    def export(cls, protocol, path, mode='w+b', *args, **kwds):
        with open(path, mode) as fp:
            cls.exportfp(protocol, fp)

    @classmethod
    def exportfp(cls, protocol, fp, *args, **kwds):
        writer = csv.writer(fp)
        cls.exportcsv(protocol, writer, *args, **kwds)

    @staticmethod
    def exportcsv(protocol, writer, encoding=DEFAULT_ENCODING):
        _encode = lambda data: unicode(data).encode(encoding)
        writer.writerows(map(lambda row: map(_encode, row),
                             protocol.dump()))
