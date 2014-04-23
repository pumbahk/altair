# -*- coding:utf-8 -*-

import os
import re
import sys
import ast
import json
sys.path.append(os.path.dirname(__file__))
from utils import abspath_from_rel
from utils import css_url_iterator

static_rx = re.compile(r"request\.static_url\((.+?)\)")
template_org_rx = re.compile(r"/templates/([^/]+)")

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

ALIAS_MAP = {
    "89ers": [], 
    "BT": ["bambitious"], 
    "bigbulls": [], 
    "CR": ["cinqreves"], 
    "NH": ["happinets"], 
    "RK": ["kings"], 
    "lakestarts": [], 
    "oxtv": ["oxtv"], 
    "ticketstar": [], 
    "vissel": []
}

class Dump(object):
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self.stdout = stdout
        self.stderr = stderr
    
class IOLikeList(list):
    def write(self, x):
        self.append(json.dumps(x, ensure_ascii=False, indent=2))

class JSONWrapper(object):
    def __init__(self, out):
        self.out = out
    def write(self, x):
        self.out.write(json.dumps(x, ensure_ascii=False, indent=2))

class CSSChange(object):
    def __init__(self, css_suffix):
        self.css_suffix = css_suffix
        self.replace_re = re.compile("\.css$")
        self.css_ext = "{}.css".format(self.css_suffix)

    def name_change(self, data):
        name = data["dst_file"]
        data["dst_file"] = self.replace_re.sub(self.css_ext, name)
        if "dst" in data:
            name = data["dst"]
            data["dst"] = self.replace_re.sub(self.css_ext, name)


app_rx = re.compile(r'([^/:\.]+?)[/:\.](?:templates|static)[/:\.]')
class DecisionMaker(object):
    def __init__(self, filename, org_name, used_css, classifier=classify, dump=None, strict=True, modules=None, css_suffix=""):
        self.filename = filename
        self.org_name = org_name
        self.classifier = classifier
        self.strict = strict
        self.dump = dump
        self.modules = modules
        self.used_css = used_css
        self._app_name = None

        ## todo: move
        self.css_change = CSSChange(css_suffix)

    @property
    def app_name(self):
        if self._app_name:
            return self._app_name
        self._app_name = self.detect_app_name(self.filename)
        return self._app_name

    def detect_app_name(self, appname):
        m = app_rx.search(appname)
        if not m:
            raise ValueError(appname)
        return m.group(1)

    def normalize_src(self, prefix, filepath):
        return filepath

    def normalize_dst(self, file_type, prefix, filepath):
        if file_type == "js":
            return self.normalize_src(prefix, filepath)

        if "js/css/" in filepath:
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
        filepath = filepath.replace("{}/".format(self.org_name), "")
        filepath = filepath.replace("static/89ers/", "static/") # for  "dst_file": "ticketing/src/altair/app/ticketing/fc_auth/static/NH/pc/89ers/style.css"

        ## device削除
        filepath = filepath.replace("{}_".format(device), "").replace("/{}".format(device), "")

        basename = os.path.basename(filepath)

        for rep in ["common", "music", "settlement"]:
            filepath = filepath.replace("images/{}".format(rep), "images")

        ## staticのprefix整理
        static_ext = 'static/{0}/{1}/'.format(self.org_name, device)
        if not file_type in os.path.splitext(filepath)[0]:
            static_ext = '{0}{1}/'.format(static_ext, file_type)

        filepath = filepath.replace("static/", static_ext)

        ## normalize basename
        basename_target = "/{}".format(basename)

        basename = basename.replace("-{}".format(self.org_name), "").replace("{}_".format(self.org_name), "").replace(self.org_name, "")
        for rep in ALIAS_MAP.get(self.org_name, []):
            basename = basename.replace("-{}".format(rep), "").replace("{}_".format(rep), "").replace(rep, "")
        if basename == ".ico":
            basename = "icon.ico" #shortcut icon
        return filepath.replace(basename_target, "/{}".format(basename))

    def module_real_path(self, prefix):
        for k, v in self.modules.items():
            prefix = prefix.replace(k, v)
        return prefix.replace(".", "/")
    
    def normalize_appname(self, target, pat):
        return target.replace(pat, self.app_name, 1)

    def info(self, spec, virtual=False):
        current_app_name = self.detect_app_name(spec)
        file_type, (prefix, filepath) = self.classifier(spec, strict=self.strict)
        dst = self.normalize_dst(file_type, prefix, filepath)
        data = {"src_file": os.path.join(self.module_real_path(prefix), self.normalize_src(prefix, filepath)), 
                "html": self.filename, 
                "src": spec, 
                "dst": self.normalize_appname(u"{}:{}".format(prefix, dst), current_app_name), 
                "org_name": self.org_name, 
                "file_type": file_type, 
                "dst_file": self.normalize_appname(os.path.join(self.module_real_path(prefix), dst), current_app_name), 
                "app_changed": current_app_name != self.app_name, 
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
        self.dump.stderr.write(data)

    def with_css(self, cssdata):
        k = cssdata["dst_file"]
        if k in self.used_css:
            return
        self.used_css[k] = 1

        self.css_change.name_change(cssdata) #rename foo.cs => foo.{suffix}.css
        self.dump.stdout.write(cssdata)
        src_dir = os.path.dirname(cssdata["src_file"])

        with open(cssdata["src_file"]) as rf:
            for url in css_url_iterator(rf):
                if url.startswith("http") and "://" in url:
                    continue
                if url.endswith(".css"):
                    file_type = "css"
                else:
                    file_type = "images"
                src_file = abspath_from_rel(url, src_dir)
                current_app_name = self.detect_app_name(src_file)
                data = {
                    "file_type": file_type, 
                    "src_file": src_file, 
                    "dst_file": self.normalize_appname(self.normalize_dst(file_type, "", src_file), current_app_name), 
                    "app_changed": current_app_name != self.app_name, 
                    "virtual": False
                }
                if file_type == "css":
                    self.with_css(data)
                else:
                    self.dump.stdout.write(data)


    def decision(self, inp):
        for line in inp:
            m = static_rx.search(line)
            if m:
                try:
                    assetspec = m.group(1)
                    path = ast.literal_eval(assetspec)
                    data = self.info(path)
                    if path.endswith(".css"):
                        self.with_css(data)
                    else:
                        self.dump.stdout.write(data)
                except Exception as e:
                    #see: e.g.altair/app/ticketing/cart/templates/BT/pc/_widgets.html
                    fmt = m.group(1)
                    if "% step" in fmt:
                        for i in [1, 2, 3, 4]:
                            assetspec = eval(fmt, {"step":i})
                            data = self.info(assetspec)
                            self.dump.stdout.write(data)
                        data = self.info(fmt, virtual=True)
                        self.dump.stdout.write(data)

                    else:
                        data = self.error(e, line, assetspec)
                        self.dump.stderr.write(data)

if __name__ == "__main__":
    css_suffix = sys.argv[1]
    cwd = sys.argv[2]

    dump = Dump(IOLikeList(), JSONWrapper(sys.stderr))
    used_css = {}
    for root, ds, fs in os.walk(cwd, topdown=False):
        for f in fs:
            if "/templates/" in root:
                path = os.path.join(root, f)
                m = template_org_rx.search(root)
                modules = {"altair.app.ticketing": "ticketing/src/altair/app/ticketing"}
                dm = DecisionMaker(path, m.group(1), used_css, dump=dump, modules=modules, css_suffix=css_suffix)
                with open(path) as rf:
                    dm.decision(rf)

    sys.stdout.write("[\n")
    sys.stdout.write((',').join(dump.stdout))
    sys.stdout.write("\n]")
