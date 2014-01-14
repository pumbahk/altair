#-*- coding: utf-8 -*-
import csv

class AugusExporter(object):
    @classmethod
    def export(cls, protocol, path, mode='w+b'):
        with open(path, mode) as fp:
            cls.exportfp(protocol, fp)

    @classmethod
    def exportfp(cls, protocol, fp):
        writer = csv.writer(fp)
        cls.exportcsv(protocol, writer)

    @staticmethod
    def exportcsv(protocol, writer):
        writer.writerows(protocol.dump())
            
