# -*- coding:utf-8 -*-

import os
import re
import sys
import ast
import json
from functools import partial

static_rx = re.compile(r"request\.static_url\((.+?)\)")
template_org_rx = re.compile(r"/templates/([^/]+)")
target = "/Users/nao/work/altair/altair/ticketing/src/altair/app/ticketing/cart/templates/vissel/pc/index.html"

dump_json=partial(json.dumps, indent=2, ensure_ascii=False)

class UnKnownFileType(Exception):
    pass

def classify(s, strict=True):
    if "static/js" in s or s.endswith(".js"):
        return ("js", s.split(":", 1))
    elif "static/css" in s or s.endswith(".css"):
        return ("css", s.split(":", 1))
    elif "static/img" or "static/images" in s:
        return ("images", s.split(":", 1))
    else:
        if strict:
            raise UnKnownFileType(s)
        return ("other", s.split(":", 1))
    
class DecisionMaker(object):
    def __init__(self, filename, org_name, classifier=classify, dump=dump_json, strict=True):
        self.filename = filename
        self.org_name = org_name
        self.classifier = classifier
        self.strict = strict
        self.dump = dump

    def normalize_src(self, prefix, filepath):
        return filepath

    def normalize_dst(self, file_type, prefix, filepath):
        if file_type == "js":
            return self.normalize_src(prefix, filepath)
        fname = self.filename
        if "/pc/" in fname or "pc_" in fname or "_pc" in fname:
            device = "pc"
        elif any(x in fname for x in ["/mb/", "mb_", "_mb", "/mobile/", "mobile_", "_mobile"]):
            device = "mobile"
        elif any(x in fname for x in ["/smartphone/", "smartphone_", "_smartphone"]):
            device = "smartphone"
        else:
            device = "pc"

        if "images_m/" in filepath or "img_m/" in filepath:
            device = "mobile"
            filepath = filepath.replace("images_m/", "images/").replace("img_m/", "images/")

        filepath = filepath.replace("/img/", "/images/")
        static_ext = 'static/{0}/{1}/'.format(self.org_name, device)
        filepath = filepath.replace("{}/".format(self.org_name), "")
        filepath = filepath.replace("static/", static_ext)
        return filepath

    def info(self, spec, virtual=False):
        file_type, (prefix, filepath) = self.classifier(spec, strict=self.strict)
        dst = self.normalize_dst(file_type, prefix, filepath)
        data = {"src_file": os.path.join(prefix.replace(".", "/"), self.normalize_src(prefix, filepath)), 
                "html": self.filename, 
                "src": spec, 
                "dst": u"{}:{}".format(prefix, dst), 
                "org_name": self.org_name, 
                "file_type": file_type, 
                "dst_file": os.path.join(prefix.replace(".", "/"), dst), 
                "virtual": virtual
        }
        return data

    def error(self, e, line, assetspec):
        data = {
            "line": line, 
            "assetspec": assetspec, 
            "filename": self.filename, 
            "error": repr(e)
        }
        sys.stderr.write(self.dump(data))
                        
    def decision(self, inp):
        for line in inp:
            m = static_rx.search(line)
            if m:
                try:
                    assetspec = m.group(1)
                    data = self.info(ast.literal_eval(assetspec))
                    sys.stdout.write(self.dump(data))
                except Exception as e:
                    #see: e.g.altair/app/ticketing/cart/templates/BT/pc/_widgets.html
                    fmt = m.group(1)
                    if "% step" in fmt:
                        for i in [1, 2, 3, 4]:
                            assetspec = eval(fmt, {"step":i})
                            data = self.info(assetspec)
                            sys.stdout.write(self.dump(data))
                        data = self.info(fmt, virtual=True)
                        sys.stdout.write(self.dump(data))

                    else:
                        data = self.error(e, line, assetspec)
                        sys.stderr.write(self.dump(data))

if __name__ == "__main__":
    cwd = sys.argv[1]
    for root, ds, fs in os.walk(cwd, topdown=False):
        for f in fs:
            if "/templates/" in root:
                path = os.path.join(root, f)
                m = template_org_rx.search(root)
                dm = DecisionMaker(path, m.group(1))
                with open(path) as rf:
                    dm.decision(rf)
