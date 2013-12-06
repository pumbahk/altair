# -*- coding:utf-8 -*-

from ctypes import *
from ctypes.util import *

gint32 = c_int32
guint32 = c_uint32
gint16 = c_int16
guint16 = c_uint16
guint = c_uint
gint = c_int
gboolean = gint
gsize = c_uint
GType = gsize
GQuark = guint32
gpointer = c_void_p
GDestroyNotify = CFUNCTYPE(None, c_void_p)
GHashFunc = CFUNCTYPE(guint, c_void_p)
GEqualFunc = CFUNCTYPE(gboolean, c_void_p, c_void_p)

class _GTypeClass(Structure):
    __fields__ = [("g_type", GType)]

class _GTypeInstance(Structure):
    __fields__ = [("g_class", _GTypeClass)]

class _GDataElt(Structure):
    __fields__ = [("key", GQuark), 
                  ("data", gpointer),
                  ("destroy", GDestroyNotify)]

class _GData(Structure):
    __fields__ = [("len", gint32), 
                  ("alloc", gint32),
                  ("data", _GDataElt * 1)]

class _GObject(Structure):
    __fields__ = [("ref_count", guint),
                  ("qdata", POINTER(_GData))]

class _PangoFontMap(Structure):
    __fields__ = [("parent_instance", _GObject)]

class _PangoFontFamily(Structure):
    __fields__ = [("parent_instance", _GObject)]

class _PangoLanguage(Structure):
    pass #xxx:?

(PANGO_DIRECTION_LTR,
  PANGO_DIRECTION_RTL,
  PANGO_DIRECTION_TTB_LTR,
  PANGO_DIRECTION_TTB_RTL,
  PANGO_DIRECTION_WEAK_LTR,
  PANGO_DIRECTION_WEAK_RTL,
  PANGO_DIRECTION_NEUTRAL
) = map(c_int, range(7))
_PangoDirection = c_int;

class _PangoDirection(Structure):
    pass

( PANGO_STYLE_NORMAL,
  PANGO_STYLE_OBLIQUE,
  PANGO_STYLE_ITALIC
) = map(c_int, range(3))
_PangoStyle = c_int
# class _PangoStyle(Structure):
#     pass

(PANGO_VARIANT_NORMAL,
 PANGO_VARIANT_SMALL_CAPS
) = map(c_int, range(2))
_PangoVariant = c_int
# class _PangoVariant(Structure):
#     pass

PANGO_WEIGHT_THIN = 100
PANGO_WEIGHT_ULTRALIGHT = 200
PANGO_WEIGHT_LIGHT = 300
PANGO_WEIGHT_BOOK = 380
PANGO_WEIGHT_NORMAL = 400
PANGO_WEIGHT_MEDIUM = 500
PANGO_WEIGHT_SEMIBOLD = 600
PANGO_WEIGHT_BOLD = 700
PANGO_WEIGHT_ULTRABOLD = 800
PANGO_WEIGHT_HEAVY = 900
PANGO_WEIGHT_ULTRAHEAVY = 1000
_PangoWeight = c_int;
# class _PangoWeight(Structure):
#     pass

(
  PANGO_STRETCH_ULTRA_CONDENSED,
  PANGO_STRETCH_EXTRA_CONDENSED,
  PANGO_STRETCH_CONDENSED,
  PANGO_STRETCH_SEMI_CONDENSED,
  PANGO_STRETCH_NORMAL,
  PANGO_STRETCH_SEMI_EXPANDED,
  PANGO_STRETCH_EXPANDED,
  PANGO_STRETCH_EXTRA_EXPANDED,
  PANGO_STRETCH_ULTRA_EXPANDED
) = map(c_int, range(9))
_PangoStretch = c_int
# class _PangoStretch(Structure):
#     pass

(
  PANGO_GRAVITY_SOUTH,
  PANGO_GRAVITY_EAST,
  PANGO_GRAVITY_NORTH,
  PANGO_GRAVITY_WEST,
  PANGO_GRAVITY_AUTO
) = map(c_int,  range(5))
_PangoGravity = c_int
# class _PangoGravity(Structure):
#     pass

(
  PANGO_GRAVITY_HINT_NATURAL,
  PANGO_GRAVITY_HINT_STRONG,
  PANGO_GRAVITY_HINT_LINE
) = map(c_int, range(3))
_PangoGravityHint = c_int;
# class _PangoGravityHint(Structure):
#     pass

class _PangoFontDescription(Structure):
    __fields__ = [("family_name", c_char_p), 
                  ("style", _PangoStyle), 
                  ("variant", _PangoVariant), 
                  ("weight", _PangoWeight), 
                  ("stretch", _PangoStretch), 
                  ("gravity", _PangoGravity), 

                  ("mask", guint16), 
                  ("static_family", guint, 1), 
                  ("size_is_absolute", guint, 1), 
                  ("size",  c_int)]


class _PangoMatrix(Structure):
    __fields__ = [("xx", c_double), 
                  ("xy", c_double), 
                  ("yx", c_double), 
                  ("yy", c_double), 
                  ("x0", c_double), 
                  ("y0", c_double), ]


class _PangoContext(Structure):
    __fields__ = [("parent_instance", _GObject), 
                  ("serial", guint), 
                  ("fontmap_serial", guint), 
                  ("set_language", POINTER(_PangoLanguage)), 
                  ("language", POINTER(_PangoLanguage)), 
                  ("base_dir", _PangoDirection), 
                  ("base_gravity", _PangoGravity), 
                  ("resolved_gravity", _PangoGravity), 
                  ("gravity_hint", _PangoGravityHint), 
                  ("font_desc", POINTER(_PangoFontDescription)), 
                  ("matrix", POINTER(_PangoMatrix),), 
                  ("font_map", POINTER(_PangoFontMap))
    ]

class _PangoFontset(Structure):
    __fields__ = [("parent_instance", _GObject)]

class _PangoFont(Structure):
    __fields__ = [("parent_instance", _GObject)]


class _GHashNode(Structure):
    __fields__ = [("key", gpointer),
                  ("value", gpointer),
                  ("key_hash", guint)]

class _GHashTable(Structure):
    __fields__ = [("size", gint), 
                  ("mod", gint), 
                  ("mask", guint), 
                  ("nnodes", gint), 
                  ("noccupied", gint), 
                  ("nodes", POINTER(_GHashNode)), 
                  ("hash_func", GHashFunc), 
                  ("key_equal_func", GEqualFunc), 
                  ("ref_count", gint), #volatile
                  ("key_destroy_func", GDestroyNotify), 
                  ("value_destroy_func", GDestroyNotify)
              ]

class _GList(Structure):
    pass
_GList.__fields__ = [("data", gpointer), 
                     ("next", _GList), 
                     ("prev", _GList)]


pango_ = None
gobject_ = None
def set_pango(pango_):
    global pango
    pango = pango_

def set_gobject(gobject_):
    global gobject
    gobject = gobject_

def get_pango():
    global pango
    return pango

def get_gobject():
    global gobject
    return gobject

def setup_ffi(pango, gobject):
    set_pango(pango)
    set_gobject(gobject)

    pango.pango_font_map_create_context.argtypes = [POINTER(_PangoFontMap)]
    pango.pango_font_map_create_context.restype = POINTER(_PangoContext)

    pango.pango_language_from_string.argtypes = [c_char_p]
    pango.pango_language_from_string.restype = POINTER(_PangoLanguage)
    pango.pango_language_to_string.argtypes = [POINTER(_PangoLanguage)]
    pango.pango_language_to_string.restype = c_char_p

    pango.pango_font_description_from_string.argtypes = [c_char_p]
    pango.pango_font_description_from_string.restype = POINTER(_PangoFontDescription)

    pango.pango_context_set_language.argtypes = [POINTER(_PangoContext), POINTER(_PangoLanguage)]
    pango.pango_context_set_language.restype = None

    pango.pango_font_map_load_fontset.argtypes = [POINTER(_PangoFontMap), POINTER(_PangoContext), POINTER(_PangoFontDescription), POINTER(_PangoLanguage)]
    pango.pango_font_map_load_fontset.restype = POINTER(_PangoFontset)

    pango.pango_fontset_get_font.argtypes = [POINTER(_PangoFontset), c_int]
    pango.pango_fontset_get_font.restype = POINTER(_PangoFont)

    pango.pango_font_describe.argtypes = [POINTER(_PangoFont)]
    pango.pango_font_describe.restype = POINTER(_PangoFontDescription)

    pango.pango_font_description_get_family.argtypes = [POINTER(_PangoFontDescription)]
    pango.pango_font_description_get_family.restype = c_char_p

    pango.pango_font_map_list_families.argtypes = [POINTER(_PangoFontMap), POINTER(POINTER(POINTER(_PangoFontFamily))), POINTER(c_int)]
    pango.pango_font_map_list_families.restype = None

    pango.pango_font_family_get_name.argtypes = [POINTER(_PangoFontFamily)]
    pango.pango_font_family_get_name.restype = c_char_p

    gobject.g_object_unref.argtypes = [gpointer]
    gobject.g_object_unref.restype = None
