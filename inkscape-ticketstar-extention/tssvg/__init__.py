# -*- coding:utf-8 -*-
import os
import sys
sys.path.append(os.path.absname(os.path.dirname(__name__)))
from collections import OrderedDict

import inkex

def is_system_windows(system_name):
    return system_name == "Windows"

class InternalFamilyNameResolver(object):
    def __init__(self, control_factory, cache):
        self.factory = control_factory
        self.cache = cache
        self.control = None

    @property
    def has_control(self):
        return self.control is not None

    def propose(self):
        self.control = self.factory()
        self.control.propose()

    def clean(self):
        if self.has_control:
            self.control.dispose()

    def resolve(self, family_name):
        try:
            return self.cache[family_name]
        except KeyError:
            self.propose()
            self.control.resolve(family_name)

class Configrator(object):
    def __init__(self, loader, finder):
        self.loader=loader
        self.finder = finder

    def maybe_ffi(self, dll_path_string):
        if isinstance(dll_path_string, basestring):
            return self.loader(self.finder(dll_path_string))
        else:
            return dll_path_string

    def setup_ffi(self, module, *args, **kwargs):
        env = {"args": args, "kwargs": kwargs}
        code = """
import {module}
{module}.setup_ffi(*args, **kwargs)
        """.format(module=module)
        exec code in env

def get_control(config, system_name):
    pango = config.maybe_ffi("libpango-1.0")
    gobject = config.maybe_ffi("libgobject-2.0")
    config.setup_ffi("ts_common_library", pango=pango, gobject=gobject)

    if is_system_windows(system_name):
        win32 = config.maybe_ffi("libpangowin32-1.0")
        config.setup_ffi("ts_win32_library", gobject=gobject, pango=pango, win32=win32)
        from .ts_win32_library import WindowsNameResolver
        return WindowsNameResolver(pango=pango, gobject=gobject, win32=win32)
    else:
        ft2 = config.maybe_ffi("libpangoft2-1.0")
        from .ts_unix_library import UnixNameResolver
        return UnixNameResolver(pango=pango, gobject=gobject, ft2=ft2)


class ReplaceMapping(object):
    def __init__(self, target_keys, convert):
        self.target_keys = target_keys
        self.convert = convert

    def __call__(self, style_dict):
        for k in self.target_keys:
            if k in style_dict:
                style_dict[k] = self.convert(style_dict[k])
        return style_dict

class TSSVGEffect(inkex.Effect):
    def __init__(self, mapping):
        inkex.Effect.__init__(self, mapping)
        self.replacer = StyleReplacer(mapping)
        self.before_output_callbacks = []

    def effect(self):
        for e in self.document.iter():
            if "style" in e.attrib:
                new_attrib = self.replacer(e.attrib["style"])
                e.attrib["style"] = new_attrib

    def add_befoure_output(self, fn):
        self.before_output_callbacks.append(fn)

    def output(self):
        """Serialize document into XML on stdout"""
        for cb in self.before_output_callbacks:
            cb(self)
        self.document.write(sys.stdout, encoding="utf-8")

class StyleReplacer(object):
    def __init__(self, use):
        self.use = use

    def __call__(self, style_string):
        return self.string_from_dict(self.use(self.dict_from_string(style_string)))

    def dict_from_string(self, string):
        return OrderedDict([[x.strip() for x in pair.split(":")]
                     for pair in string.split(";") if pair])

    def string_from_dict(self, D):
        return u"; ".join(u":".join((unicode(k), unicode(v))) for k, v in D.items())
