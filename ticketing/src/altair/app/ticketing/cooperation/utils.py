#-*- coding: utf-8 -*-
import collections
from altair.app.ticketing import newRootFactory

def add_routes(config, route_url_resource):
    for route, values in route_url_resource.items():
        url, resource_class = values
        kwds = {}
        if resource_class:
            kwds['factory'] = newRootFactory(resource_class)
        config.add_route(route, url, **kwds)


import re

class DuplicateInstallError(Exception):
    pass

class CSVEmptyError(Exception):
    pass

class RequestAccessor(object):
    in_params = {}
    in_matchdict = {}

    _regx_all = re.compile('^(?P<name>\S+)_all$')
    def __init__(self, request):
        self._validate()
        self._request = request

    def _validate(self):
        all_names = self.in_params.keys() + self.in_matchdict.keys()
        error_names = [name for name in all_names if all_names.count(name) != 1 or all_names.count(name+'_all') != 0]
        if error_names:
            raise DuplicateInstallError('Duplicate installed: {} in {}'.format(
                error_names, self.__class__.__name__))

    def __getattr__(self, name):
        if name in self.in_matchdict:
            type_ = self.in_matchdict[name]
            value = self._request.matchdict[name]
            return type_(value)
        elif name in self.in_params:
            type_ = self.in_params[name]
            value = self._request.params.get(name)
            return type_(value)

        match = self._regx_all.match(name)
        if match:
            name = match.group('name')

            if name in self.in_matchdict:
                type_ = self.in_matchdict[name]
                values = [self._request.matchdict[name]]
                return map(type_, values)
            elif name in self.in_params:
                type_ = self.in_params[name]
                values = self._request.params.getall(name)
                return map(type_, values)
        raise AttributeError(name)

import csv
import datetime

DEFAULT_ENCODING = 'cp932'

class RawType(type):
    encoding = DEFAULT_ENCODING

    @classmethod
    def encode(cls, value):
        return value

    @classmethod
    def decode(cls, value):
        return value

class UnicodeType(RawType):
    @classmethod
    def encode(cls, value):
        return value.encode(cls.encoding)

    @classmethod
    def decode(cls, value):
        return value.decode(cls.encoding)

class IntegerType(RawType):
    @classmethod
    def encode(cls, value):
        return str(value) if not (value is None) and (value.isdigit()) else ''

    @classmethod
    def decode(cls, value):
        return int(value) if not (value is '') and (value.isdigit()) else None


class DateTimeType(RawType):
    FORMAT = '%Y/%m/%d %H:%M:%S'
    @classmethod
    def encode(cls, value):
        return datetime.datetime.strftime(value, cls.FORMAT) if value else ''

    @classmethod
    def decode(cls, value):
        return datetime.datetime.strptime(value, cls.FORMAT) if value else None

class Record(dict):
    fields = collections.OrderedDict()

    def __init__(self):
        self._install_attributes()

    def _install_attributes(self):
        for key in self.fields.keys():
            setattr(self, key, '')

    @classmethod
    def headers(cls):
        return cls.fields.keys()

    @classmethod
    def get_key(cls, idx):
        return cls.fields.keys()[idx] # raise IndexError

    def parse(self, row):
        for ii, (key, type_) in enumerate(self.fields.items()):
            data = row[ii]
            data = type_.decode(data)
            setattr(self, key, data)

    def row(self):
        return [type_.encode(getattr(self, key))
                for key, type_ in self.fields.iteritems()]

    def __getitem__(self, idx):
        key = self.get_key(idx)
        try:
            return getattr(self, key)
        except AttributeError as err:
            raise IndexError(err)

    def __setitem__(self, idx, value):
        key = self.get_key(idx)
        try:

            return setattr(self, key, value)
        except AttributeError as err:
            raise IndexError(err)

class CSVData(list):
    record_factory = Record
    encoding = 'utf8'

    def install(self, record_factory):
        self.record_factory = record_factory

    def read_csv(self, filename_or_fp, encoding=None):
        try:
            with open(filename_or_fp) as fp:
                self._parse(fp)
        except TypeError as err: # file object
            fp = filename_or_fp
            self._parse(fp)

    def write_csv(self, filename_or_fp):
        try:
            with open(filename_or_fp) as fp:
                self._write(fp)
        except TypeError as err: # file object
            fp = filename_or_fp
            self._write(fp)

    def _parse(self, fp):
        reader = csv.reader(fp)
        try:
            reader.next() # header
        except StopIteration as err:
            raise CSVEmptyError()

        for row in reader:
            record = self.record_factory()
            record.parse(row)
            self.append(record)

    def _write(self, fp):
        writer = csv.writer(fp, delimiter=',')
        row = ''
        try:
            headers = self.record_factory.headers()
            writer.writerow(headers)
            for record in self:
                row = record.row()
                writer.writerow(row)
        except UnicodeError as err:
            raise err.__class__(repr(row), *err.args[1:])
