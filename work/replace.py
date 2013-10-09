# -*- coding:utf-8 -*-
import json
import tempfile
import os.path
import cssutils
import logging
from collections import OrderedDict
import sys
from utils import abspath_from_rel

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
        self.dst_from_src = {}

    def parse(self, xs):
        for D in xs:
            if not D["virtual"]:
                self.mv_events.add(D["src_file"], D["dst_file"])
                if D["file_type"] == "css":
                    self.css_events.add(D["src_file"], D["dst_file"])
            if "src" in D and "dst" in D:
                self.sed_events.add(D["html"], (D["src"], D["dst"]))
            self.dst_from_src[D["src_file"]] = D["dst_file"]
        return self

def escape_for_sed(x):
    return x.replace(".", "\.").replace("/", "\/")

parsers = {}
def get_css_parser(target):
    global parsers
    if target in parsers:
        return parsers[target], False
    
    ## suppress logging message
    parser = cssutils.CSSParser(loglevel=logging.CRITICAL).parseFile(target, validate=False)
    parsers[target] = parser
    return parser, True



class CSSReplacer(object):
    def __init__(self, src_css, dst_css, dst_from_src):
        self.src_css = src_css
        self.dst_css = dst_css 
        self.dst_from_src = dst_from_src
        self.src_css_dir = os.path.dirname(self.src_css)

    def replace_url(self, src_img_rel):
        src_img = abspath_from_rel(src_img_rel, self.src_css_dir)
        dst_img = self.dst_from_src[src_img]
        return os.path.relpath(dst_img, self.dst_css)

    def replace(self, target, outname):
        css, created = get_css_parser(target) #href=None?
        if not created:
            return 
        def replacer(url):
            return self.replace_url(url)
        cssutils.replaceUrls(css, replacer, ignoreImportRules=True)
        with open(outname, "w") as wf:
            wf.write(css.cssText)
        
def execute(app):
    for html, vs in app.sed_events:
        for (src, dst) in vs:
            if src == dst:
                sys.stderr.write("skip:{}".format(src))
                sys.stderr.write("\n")
                continue
            print "gsed -i 's/{src}/{dst}/g;' {html}".format(html=html, src=escape_for_sed(src), dst=escape_for_sed(dst))
    print "git commit -a -m 'template edit'"
    for k, vs in app.mv_events:
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

def css_execute(app):
    for src, vs in app.css_events:
        for dst in vs:
            replacer = CSSReplacer(src, dst, app.dst_from_src)
            try:
                outname = tempfile.mktemp()
                replacer.replace(src, outname)
                print "mv {outname} {dst}".format(outname=outname, dst=dst)
            except KeyError as e:
                for k in app.dst_from_src.keys():
                    print k
                raise 
            except Exception as e:
                pass


if __name__ == "__main__":
    with open(sys.argv[1]) as rf:
        app = App().parse(json.load(rf))
        execute(app)
        css_execute(app)
