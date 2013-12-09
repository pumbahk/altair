# -*- coding:utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
# from collections import OrderedDict 
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
        if not self.has_control:
            self.control = self.factory()
            self.control.propose()

    def clean(self, wrapper):
        if self.has_control:
            self.control.dispose()

    def resolve(self, family_name):
        family_name = force_unicode(family_name)
        try:
            return self.cache[family_name]
        except KeyError:
            self.propose()
            family_name_internal = self.control.resolve(family_name)
            family_name_internal = force_unicode(family_name_internal)
            self.cache[family_name] = family_name_internal
            return family_name_internal

def force_unicode(s):
    if isinstance(s, unicode):
        return s
    elif hasattr(s, "decode"):
        return s.decode("utf-8")
    else:
        raise Exception("Invalida arguments: %s",  s)

class Configurator(object):
    def __init__(self, loader, finder):
        self.loader=loader
        self.finder = finder

    def maybe_ffi(self, dll_path_string):
        if isinstance(dll_path_string, basestring):
            return self.loader(self.finder(dll_path_string))
        else:
            return dll_path_string

    def include_resolver(self, fn, *args, **kwargs):
        resolver = fn(self, *args, **kwargs)
        for ffi in kwargs.keys():
            assert getattr(self, ffi)
        return resolver

def get_control(config, system_name):
    from .ffi_library import IncludeFFI
    pango = config.maybe_ffi("libpango-1.0")
    gobject = config.maybe_ffi("libgobject-2.0")
    if is_system_windows(system_name):
        win32 = config.maybe_ffi("libpangowin32-1.0")
        assert win32
        return config.include_resolver(IncludeFFI.include_windows, pango=pango, gobject=gobject, win32=win32)
    else:
        ft2 = config.maybe_ffi("libpangoft2-1.0")
        return config.include_resolver(IncludeFFI.include_unix, pango=pango, gobject=gobject, ft2=ft2)

class ReplaceMapping(object):
    def __init__(self, target_keys, convert):
        self.target_keys = target_keys
        self.convert = convert

    def __call__(self, style_dict):
        arr = []
        for k, v in style_dict:
            if k in self.target_keys:
                v = self.convert(v)
            arr.append((k,v))
        return arr

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
        return self.string_from_pairs(self.use(self.pairs_from_string(style_string)))

    def pairs_from_string(self, string):
        return [[x.strip() for x in pair.split(":")]
                     for pair in string.split(";") if pair]

    def string_from_pairs(self, pairs):
        return u"; ".join(u":".join((k, v)) for k, v in pairs)
