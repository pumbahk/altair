# -*- coding:utf-8 -*-

class IdNameLabelMapping(object):
    """
    e.g. id, name, label
    ----------------------
         1,  music,  音楽
         2,  stage,  演劇
    """
    def __init__(self):
        self.name_to_id = {}
        self.id_to_name = {}
        self.id_to_label = {}
        self.name_to_label = {}

    def add(self, i, name, label):
        self.id_to_name[i] = name
        self.id_to_label[i] = label
        self.name_to_label[name] = label
        self.name_to_id[name] = i

    @classmethod
    def from_choices(cls, choices):
        instance = cls()
        for i, (name, label) in enumerate(choices):
            instance.add(i, name, label)
        return instance

    @classmethod
    def from_sequence(cls, seq):
        instance = cls()
        for i, name, label in seq:
            instance.add(i, name, label)
        return instance

    def dump_as_choices(self, names):
        return [(name, self.name_to_label[name]) for name in names]

    def dump_as_sequence_from_names(self, names):
        return [(self.name_to_id[name], name, self.name_to_label[name]) for name in names]

