#-*- coding: utf-8 -*-
import csv

class AugusExporter(object):
    @classmethod
    def export(cls, protocol, path):
        with open(path, 'rb') as fp:
            self.exportfp(protocol, fp)

    @classmethod
    def exportfp(cls, protocol, fp):
        writer = csv.writer(fp)
        self.exportcsv(protocol, writer)

    @classmethod
    def exportcsv(cls, protocol, writer):
        writer.writerows(protocol.dump())
            
