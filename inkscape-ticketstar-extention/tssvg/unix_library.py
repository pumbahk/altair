# -*- coding:utf-8 -*-

from ctypes import *
from ctypes.util import *

ft2 = None
def set_ft2(ft2_):
    global ft2
    ft2 = ft2_

def get_ft2():
    global ft2
    return ft2

def setup_ffi(_ft2):
    global ft2
    ft2 = _ft2
    ft2.pango_ft2_font_map_new.argtypes = []
    ft2.pango_ft2_font_map_new.restype = POINTER(_PangoFontMap)

class UnixNameResolver(object):
    def __init__(self):
        self.lang = None

    def using(self):
        self.propose()
        self.gobject = get_gobject()
        self.pango = get_pango()
        self.ft2 = get_ft2()
        yield self
        self.dispose()

    def propose(self):
        self.gobject = get_gobject()
        self.pango = get_pango()
        self.ft2 = get_ft2()

        ft2 = self.ft2
        pango = self.pango
        self.fontmap = ft2.pango_ft2_font_map_new()
        self.context = pango.pango_font_map_create_context(self.fontmap)

    def dispose(self):
        gobject = self.gobject
        gobject.g_object_unref(self.fontmap)
        gobject.g_object_unref(self.context)

    def resolve(self, family_name, lang=None):
        gobject = self.gobject
        pango = self.pango
        lang = lang or self.lang

        desc = pango.pango_font_description_from_string(family_name)
        pango.pango_context_set_language(self.context, lang)
        fontset = pango.pango_font_map_load_fontset(self.fontmap, self.context, desc, en)
        font = pango.pango_fontset_get_font(fontset, 72)
        family_name_internal = pango.pango_font_description_get_family(pango.pango_font_describe(font))

        gobject.g_object_unref(font)
        gobject.g_object_unref(fontset)
        return family_name_internal
