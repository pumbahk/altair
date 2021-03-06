# -*- coding:utf-8 -*-
import json
import os.path
from collections import OrderedDict, defaultdict
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
    def __init__(self):
        self.sed_events = EventQueue()
        self.css_events = EventQueue()
        self.mv_events = EventQueue()
        self.dst_from_src = defaultdict(list)

    def parse(self, xs):
        for D in xs:
            if not D["virtual"]:
                self.mv_events.add(D["src_file"], (D["dst_file"], D["app_changed"]))
                if D["file_type"] == "css":
                    self.css_events.add(D["src_file"], D["dst_file"])
            if "src" in D and "dst" in D:
                self.sed_events.add(D["html"], (D["src"], D["dst"]))
            self.dst_from_src[D["src_file"]].append(D["dst_file"])
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

    def new_relative_url(self, src_img_rel, dst_base):
        try:
            src_img = abspath_from_rel(src_img_rel, self.src_css_dir)

            ## xxx:
            dst_candidates = self.dst_from_src[src_img]
            max_len = 0
            dst_img = object() #boo
            for c in dst_candidates:
                matched_len = len(os.path.commonprefix([c, dst_base]))
                if max_len < matched_len:
                    dst_img = c
                    max_len = matched_len
            return os.path.relpath(dst_img, self.dst_css_dir)
        except (AttributeError):
            sys.stderr.write("sorry. not found. src={0} rel={1}\n".format(src_img, src_img_rel))
            return None

    def replaced_iter(self, target, dst_base):
        used = {}
        with open(target) as rf:
            for img_rel in css_url_iterator(rf):
                if img_rel.startswith("http") and "://" in img_rel:
                    continue
                if img_rel in used:
                    continue
                used[img_rel] = 1
                new_relative_url = self.new_relative_url(img_rel, dst_base)
                if new_relative_url:
                    yield img_rel, new_relative_url

import re
before_device_rx = re.compile(r'.+(mobile|pc)')
before_rel_file_dir_rx = re.compile(r'[^:]+:')
sed_cache = set()
def execute(app):
    for html, vs in app.sed_events:
        for (src, dst) in vs:
            if src == dst:
                sys.stderr.write("skip:{}".format(src))
                sys.stderr.write("\n")
                continue
            src_pattern = escape_for_sed(before_rel_file_dir_rx.sub("", src))
            dst_rep = escape_for_sed(before_device_rx.sub(lambda m: m.group(1), dst))
            command = 'sed -i "s/{src}/{dst}/g;" {html}'.format(html=html, src=src_pattern, dst=dst_rep)
            if not command in sed_cache:
                print command
                sed_cache.add(command)
    print "git commit -a -m 'template edit'"
    for k, vs in app.mv_events:
        used = {}
        for v, app_changed in vs:
            if k == v:
                sys.stderr.write("skip:{}".format(k))
                sys.stderr.write("\n")
                continue
            if not k in used and not app_changed:
                print "mkdir -p `dirname {v}` && git mv {k} {v}".format(k=k, v=v)
                used[k] = v
            else:
                print "mkdir -p `dirname {v}` && cp {k} {v} && git add {v}".format(k=used.get(k, k), v=v)

def css_execute(app):
    used = {}
    for src, vs in app.css_events:
        for dst in vs:
            if dst in used:
                continue
            used[dst] = 1
            try:
                replacer = CSSReplacer(src, dst, app.dst_from_src)
                for pat, rep in replacer.replaced_iter(src, dst):
                    if pat != rep:
                        print 'sed -i "s/{pat}/{rep}/g;" {dst}'.format(dst=dst, pat=escape_for_sed(pat), rep=escape_for_sed(rep))
            except IOError:
                sys.stderr.write("skip: No Such file {}\n".format(src))


if __name__ == "__main__":
    with open(sys.argv[1]) as rf:
        app = App().parse(json.load(rf))
        execute(app)
        css_execute(app)
