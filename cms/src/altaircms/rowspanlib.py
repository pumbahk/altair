from collections import defaultdict
from collections import namedtuple
import copy
import itertools

class MapperForRowspan(object):
    def __init__(self, mapping, keyfn):
        self.mapping = mapping
        self.mapping_key = keyfn

PartObject = namedtuple("PartObject", "rowspan values")

class RowSpanGrid(object):
    def __init__(self):
        self.mappers_pair = [] #(mapper, gid)

    def register(self, name, mapper=None, mapping=None, keyfn=None):
        assert mapper or (mapping and keyfn)
        if mapper and hasattr(mapper, "mapping"):
            self.mappers_pair.append((name, mapper))
        else:
            self.mappers_pair.append((name, MapperForRowspan(mapping, keyfn)))

    def create(self, source, with_raw=False):
        pairs = copy.copy(self.mappers_pair)
        return RowSpanGridIteratorFactory(pairs, source, with_raw=with_raw).create()

def dict_list():
    return defaultdict(list)
def dict_int():
    return defaultdict(int)

class RowSpanGridIteratorFactory(object):
    def __init__(self, gid_mapper_pairs, source, with_raw=False):
        self.gid_mapper_pairs = gid_mapper_pairs
        self.source = list(source)
        self.rowspan_dict = None
        self.rows = []
        self.with_raw = with_raw

    def configure(self):
        if self.rows and self.rowspan_dict:
            return 
        rowspan_keys = defaultdict(lambda : None)
        rowspan_dict = defaultdict(dict_list)

        for source_row in self.source:
            row = []
            for gid, mapper in self.gid_mapper_pairs:
                k = mapper.mapping_key(source_row)

                changed = rowspan_keys[gid] != k
                if changed:
                    rowspan_dict[gid][k].append(1)
                else:
                    rowspan_dict[gid][k][-1] += 1

                mapped = mapper.mapping(source_row, k, changed)

                rowspan_keys[gid] = k
                row.append((gid, k, mapped))
            self.rows.append(row)
        self.rowspan_dict = rowspan_dict

    def create(self):
        self.configure()
        if self.with_raw:
            return RowSpanGridIteratorWithRaw(self.rows, self.rowspan_dict, self.source)
        else:
            return RowSpanGridIterator(self.rows, self.rowspan_dict)

class RowSpanGridIterator(object):
    def __init__(self, rows, rowspan_dict):
        self.rows = rows
        self.rowspan_dict = rowspan_dict

    def __iter__(self):
        rowspan_keys = defaultdict(lambda : None)
        rowspan_counter = defaultdict(dict_int)
        for row in self.rows:
            args = []
            for gid, k, mapped in row:
                if rowspan_keys[gid] != k:
                    i = rowspan_counter[gid][k]
                    rowspan = self.rowspan_dict[gid][k][i]
                    rowspan_counter[gid][k] += 1
                else:
                    rowspan = 0
                rowspan_keys[gid] = k
                if mapped:
                    args.append(PartObject(rowspan=rowspan, values=mapped))
                else:
                    args.append(None)
            yield args

class RowSpanGridIteratorWithRaw(object):
    def __init__(self, rows, rowspan_dict, source):
        self.rows = rows
        self.rowspan_dict = rowspan_dict
        self.source = source

    def __iter__(self):
        rowspan_keys = defaultdict(lambda : None)
        rowspan_counter = defaultdict(dict_int)
        for row, raw_row in itertools.izip(self.rows, self.source):
            args = []
            for gid, k, mapped in row:
                if rowspan_keys[gid] != k:
                    i = rowspan_counter[gid][k]
                    rowspan = self.rowspan_dict[gid][k][i]
                    rowspan_counter[gid][k] += 1
                else:
                    rowspan = 0
                rowspan_keys[gid] = k
                if mapped:
                    args.append(PartObject(rowspan=rowspan, values=mapped))
                else:
                    args.append(None)
            args.append(raw_row)
            yield args
