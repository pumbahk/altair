# -*- coding:utf-8 -*-
"""
csv:
top, child, grand-child, name
"""

class Context(object):
    def __init__(self, data, i=0):
        self.i = i
        self.current = data

    def current_row(self, i):
        pass

import csv
def parse_row(context, row, n=3):
    for i in xrange(n):
        if row[i] == "":
            context = context["children"][-1]
        else:
            if not "children" in context:
                context["children"] = []
            context["children"].append(dict(label=row[i].decode("utf-8"), name=row[-1].decode("utf-8")))
            break

def parse(rf, n=3):
    context = dict(name=u"top", label=u"トップ")
    for row in  csv.reader(rf):
        parse_row(context, row, n=n)
    return context

import json
import codecs

if __name__ == "__main__":
    with open("genre.csv") as rf:
        with codecs.open("genre.json", "w", "utf-8") as wf:
            json.dump(parse(rf), wf, indent=2, ensure_ascii=False)
        
