# encoding: utf-8

import math
import sys
import struct
import collections

DEFAULT_INITIAL_CAPACITY = 16
MAXIMUM_CAPACITY = 1 << 30
DEFAULT_LOAD_FACTOR = 0.75

class JavaHasher(object):
    def __init__(self, system_encoding=sys.getdefaultencoding()):
        self.system_encoding = system_encoding

    def calculateHashForUnicode(self, uni):
        utf16 = uni.encode("UTF-16BE")
        off = 0
        l = len(utf16)
        h = 0
        while off < l:
            v = struct.unpack(">H", utf16[off:off + 2])[0]
            off += 2
            h = (31 * h + v) & 0xffffffff
        return h;

    def __call__(self, obj):
        if isinstance(obj, str):
            return self.calculateHashForUnicode(unicode(obj, self.system_encoding))
        elif isinstance(obj, unicode):
            return self.calculateHashForUnicode(obj)
        raise NotImplemented()

class JavaHashMap(object):
    class Entry(tuple):
        __slot__ = ()

        def __new__(self, key, value, h, prev, next):
            instance = tuple.__new__(self, (key, value))
            instance.h = h
            instance.prev = prev
            instance.next = next
            return instance

        @property
        def key(self):
            return self[0]

        @property
        def value(self):
            return self[1]

    def __init__(self, initial_capacity=DEFAULT_INITIAL_CAPACITY, load_factor=DEFAULT_LOAD_FACTOR, hasher=JavaHasher()):
        if initial_capacity > MAXIMUM_CAPACITY:
            initial_capacity = MAXIMUM_CAPACITY
        if load_factor <= 0 or math.isnan(load_factor):
            raise ValueError("Illegal load factor: " + load_factor)

        capacity = 1
        while capacity < initial_capacity:
            capacity <<= 1

        self.load_factor = load_factor;
        self.threshold = int(capacity * load_factor)
        self.buckets = [None] * capacity

        def hash(obj):
            h = hasher(obj)
            h ^= (h >> 20) ^ (h >> 12)
            return h ^ (h >> 7) ^ (h >> 4)

        self.hasher = hash
        self.mod_count = 0
        self.size = 0

    def index_for(self, h, length):
        return h & (length - 1)

    def rehash(self, new_capacity):
        if len(self.buckets) == MAXIMUM_CAPACITY:
            return
        new_buckets = [None] * new_capacity
        for entry in self.buckets:
            while entry is not None:
                next = entry.next
                i = self.index_for(entry.h, new_capacity)
                entry.next = new_buckets[i]
                new_buckets[i] = entry
                entry = next
        self.buckets = new_buckets
        self.threshold = int(new_capacity * self.load_factor)

    def find_entry(self, key):
        if key is None:
            entry = self.buckets[0]
            while entry is not None:
                if entry.key is None:
                    return entry
                entry = entry.next
        else:
            h = self.hasher(key)
            i = self.index_for(h, len(self.buckets))
            entry = self.buckets[i]
            while entry is not None:
                if entry.h == h and entry.key == key:
                    return entry
                entry = entry.next
        return None

    def __setitem__(self, key, value):
        if key is None:
            entry = self.buckets[0]
            while entry is not None:
                if entry.key is None:
                    old_value = entry.value
                    new_entry = self.Entry(key, value, 0, entry.prev, entry.next)
                    if entry.prev is None:
                        self.buckets[0] = new_entry
                    else:
                        entry.prev.next = new_entry
                    if entry.next is not None:
                        entry.next.prev = new_entry
                    entry.value = value
                    return old_value
                entry = entry.next

            new_entry = self.Entry(key, value, h, None, self.buckets[0])
            if new_entry.next is not None:
                new_entry.next.prev = entry
            self.buckets[0] = new_entry

            if self.size >= self.threshold:
                self.rehash(2 * len(self.buckets))
            self.size += 1
        else:
            h = self.hasher(key)
            i = self.index_for(h, len(self.buckets))
            entry = self.buckets[i]
            while entry is not None:
                if entry.h == h and entry.key == key:
                    old_value = entry.value
                    new_entry = self.Entry(key, value, h, entry.prev, entry.next)
                    if entry.prev is None:
                        self.buckets[i] = new_entry
                    else:
                        entry.prev.next = new_entry
                    if entry.next is not None:
                        entry.next.prev = new_entry
                    return old_value
                entry = entry.next

            self.mod_count += 1

            new_entry = self.Entry(key, value, h, None, self.buckets[i])
            if new_entry.next is not None:
                new_entry.next.prev = entry
            self.buckets[i] = new_entry

            if self.size >= self.threshold:
                self.rehash(2 * len(self.buckets))
            self.size += 1
        return None

    def __getitem__(self, key):
        entry = self.find_entry(key)
        return None if entry is None else entry.value

    def iteritems(self):
        i = 0
        while i < len(self.buckets):
            entry = self.buckets[i]
            while entry is not None:
                yield entry
                entry = entry.next
            i += 1

    def iterkeys(self):
        for entry in self.iteritems():
            yield entry.key

    def __iter__(self):
        return self.iterkeys()