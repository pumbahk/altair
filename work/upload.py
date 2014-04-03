# -*- coding:utf-8 -*-
# -*- coding:utf-8 -*-
import json
import os.path
from collections import OrderedDict
import sys
sys.path.append(os.path.dirname(__file__))
from utils import abspath_from_rel
from utils import css_url_iterator

class EventQueue(object):
    def __init__(self):
        self.q = OrderedDict()

    def add(self, k, v):
        if not k in self.q:
            self.q[k] = []
        if not v in self.q[k]: #O(n)
            self.q[k].append(v)

    def __iter__(self):
        return iter(self.q.items())

class App(object):
    def __init__(self, s3prefix):
        self.s3prefix = s3prefix
        self.sed_events = EventQueue()
        self.css_events = EventQueue()
        self.mv_events = EventQueue()
        self.dst_from_src = {}

    def parse(self, xs):
        for D in xs:
            if not D["virtual"]:
                self.mv_events.add(D["src_file"], (D["dst_file"], D["app_changed"]))
                if D["file_type"] == "css":
                    self.css_events.add(D["src_file"], D["dst_file"])
            if "src" in D and "dst" in D:
                self.sed_events.add(D["html"], (D["src"], D["dst"]))
            self.dst_from_src[D["src_file"]] = D["dst_file"]
        return self

def escape_for_sed(x):
    return x.replace(".", "\.").replace("/", "\/")

class CSSReplacer(object):
    def __init__(self, src_css, dst_css, dst_from_src):
        self.src_css = src_css
        self.dst_css = dst_css 
        self.dst_from_src = dst_from_src
        self.src_css_dir = os.path.dirname(self.src_css)
        self.dst_css_dir = os.path.dirname(self.dst_css)

    def new_relative_url(self, src_img_rel):
        src_img = abspath_from_rel(src_img_rel, self.src_css_dir)
        dst_img = self.dst_from_src[src_img]
        return os.path.relpath(dst_img, self.dst_css_dir)

    def replaced_iter(self, target):
        used = {}
        with open(target) as rf:
            for img_rel in css_url_iterator(rf):
                if img_rel.startswith("http") and "://" in img_rel:
                    continue
                if img_rel in used:
                    continue
                used[img_rel] = 1
                yield img_rel, self.new_relative_url(img_rel)


import re
rx = re.compile(r"^.+/(.+)/static")
def strip_physical_directory_path(x):
    return rx.sub(lambda m : m.group(1)+"/static", x)

def execute(app):
    for k, vs in app.mv_events:
        used = {}
        striped_k = strip_physical_directory_path(k)
        for v, app_changed in vs:
            v = strip_physical_directory_path(v)
            if striped_k == v:
                sys.stderr.write("skip:{}".format(k))
                sys.stderr.write("\n")
                continue
            if not k in used and not app_changed:
                print "s3cmd -P put {k} s3://{app.s3prefix}{v}".format(k=k, v=v, app=app)
                used[k] = v
            else:
                print "s3cmd -P put {k} s3://{app.s3prefix}{v}".format(k=k, v=v, app=app)


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        sys.stderr.write("<> <foo.json> <s3prefix>")
    with open(sys.argv[1]) as rf:
        app = App(sys.argv[2]).parse(json.load(rf))
        execute(app)
