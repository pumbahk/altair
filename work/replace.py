# -*- coding:utf-8 -*-
import json
from collections import OrderedDict
import sys

class UpdateManager(object):
    def __init__(self, target):
        self.target = target
        self.q = []

class EventQueue(object):
    def __init__(self):
        self.q = OrderedDict()

    def add(self, k, v):
        if not k in self.q:
            self.q[k] = set()
        if not v in self.q[k]:
            self.q[k].add(v)

    def __iter__(self):
        return iter(self.q.items())

class App(object):
    def __init__(self):
        self.file_events = EventQueue()
        self.fs_events = EventQueue()

    def parse(self, xs):
        for D in xs:
            if not D["virtual"]:
                self.fs_events.add(D["src_file"], D["dst_file"])
            self.file_events.add(D["html"], (D["src"], D["dst"]))
        return self

def normalize_for_sed(x):
    return x.replace(".", "\.").replace("/", "\/")

def execute(app):
    for html, vs in app.file_events:
        for (src, dst) in vs:
            if src == dst:
                sys.stderr.write("skip:{}".format(src))
                sys.stderr.write("\n")
                continue
            print "gsed -i 's/{src}/{dst}/g;' {html}".format(html=html, src=normalize_for_sed(src), dst=normalize_for_sed(dst))
    print "git commit -a -m 'template edit'"
    for k, vs in app.fs_events:
        used = {}
        for v in vs:
            if k == v:
                sys.stderr.write("skip:{}".format(k))
                sys.stderr.write("\n")
                continue
            if not k in used:
                print "mkdir -p `dirname {v}` && git mv {k} {v}".format(k=k, v=v)
                used[k] = v
            else:
                print "mkdir -p `dirname {v}` && cp {k} {v} && git add {v}".format(k=used[k], v=v)

if __name__ == "__main__":
    with open(sys.argv[1]) as rf:
        app = App().parse(json.load(rf))
        execute(app)
