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


class IncludeFFI(object):
    @classmethod
    def include_common(cls, config, pango, gobject):
        assert pango
        assert gobject
        config.pango = pango
        config.gobject = gobject

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

    @classmethod
    def include_unix(cls, config, pango, gobject, ft2):
        cls.include_common(config, pango, gobject)
        ft2.pango_ft2_font_map_new.argtypes = []
        ft2.pango_ft2_font_map_new.restype = POINTER(_PangoFontMap)
        config.ft2 = ft2

        class UnixNameResolver(object):
            def __init__(self, gobject, pango, ft2):
                self.gobject = gobject
                self.pango = pango
                self.ft2 = ft2
                self.lang = None

            def propose(self):
                ft2 = self.ft2
                pango = self.pango
                self.fontmap = ft2.pango_ft2_font_map_new()
                self.context = pango.pango_font_map_create_context(self.fontmap)

            def dispose(self):
                gobject = self.gobject
                gobject.g_object_unref(self.fontmap)
                gobject.g_object_unref(self.context)

            def resolve(self, family_name, lang=None):
                family_name = family_name.encode("utf-8")
                gobject = self.gobject
                pango = self.pango
                lang = lang or self.lang
                if lang is None:
                    lang = self.lang = pango.pango_language_from_string(c_char_p("en-US")) #xxx:

                desc = pango.pango_font_description_from_string(family_name)
                pango.pango_context_set_language(self.context, lang)
                fontset = pango.pango_font_map_load_fontset(self.fontmap, self.context, desc, lang)
                font = pango.pango_fontset_get_font(fontset, 72)
                family_name_internal = pango.pango_font_description_get_family(pango.pango_font_describe(font))

                gobject.g_object_unref(font)
                gobject.g_object_unref(fontset)
                return family_name_internal
        return UnixNameResolver(pango=pango, gobject=gobject, ft2=ft2)


    @classmethod
    def include_windows(cls, config, pango, gobject, win32):
        from ctypes import wintypes
        assert win32
        cls.include_common(config, pango, gobject)
        ## definition
        class _PangoWin32FontCache(Structure):
            __fields__ = [("forward", POINTER(_GHashTable)), 
                          ("back", POINTER(_GHashTable)), 
                          ("mru", POINTER(_GList)), 
                          ("mru_tail", POINTER(_GList)), 
                          ("mru_count", c_int)
            ]

        ## http://www.math.uiuc.edu/~gfrancis/illimath/windows/aszgard_mini/bin/MinGW/include/wingdi.h
        LF_FACESIZE = 32
        LF_FULLFACESIZE        = 64
        DEFAULT_CHARSET         = 1
        SYMBOL_CHARSET        = 2
        SHIFTJIS_CHARSET = 128

        class _LOGFONT(Structure):
            _fields_ = [
                ('lfHeight', c_long),
                ('lfWidth', c_long),
                ('lfEscapement', c_long),
                ('lfOrientation', c_long),
                ('lfWeight', c_long),
                ('lfItalic', c_byte),
                ('lfUnderline', c_byte),
                ('lfStrikeOut', c_byte),
                ('lfCharSet', c_byte),
                ('lfOutPrecision', c_byte),
                ('lfClipPrecision', c_byte),
                ('lfQuality', c_byte),
                ('lfPitchAndFamily', c_byte),
                ('lfFaceName', (c_char * LF_FACESIZE))  # Use ASCII
            ]

        class _LOGFONTW(Structure):
            _fields_ = [
                ('lfHeight', c_long),
                ('lfWidth', c_long),
                ('lfEscapement', c_long),
                ('lfOrientation', c_long),
                ('lfWeight', c_long),
                ('lfItalic', c_byte),
                ('lfUnderline', c_byte),
                ('lfStrikeOut', c_byte),
                ('lfCharSet', c_byte),
                ('lfOutPrecision', c_byte),
                ('lfClipPrecision', c_byte),
                ('lfQuality', c_byte),
                ('lfPitchAndFamily', c_byte),
                ('lfFaceName', (c_wchar * LF_FACESIZE))  # Use unicode
            ]

        class _TEXTMETRIC(Structure):
            _fields_ = [
                ('tmHeight', c_long),
                ('tmAscent', c_long),
                ('tmDescent', c_long),
                ('tmInternalLeading', c_long),
                ('tmExternalLeading', c_long),
                ('tmAveCharWidth', c_long),
                ('tmMaxCharWidth', c_long),
                ('tmWeight', c_long),
                ('tmOverhang', c_long),
                ('tmDigitizedAspectX', c_long),
                ('tmDigitizedAspectY', c_long),
                ('tmFirstChar', c_char),  # Use ASCII
                ('tmLastChar', c_char),
                ('tmDefaultChar', c_char),
                ('tmBreakChar', c_char),
                ('tmItalic', c_byte),
                ('tmUnderlined', c_byte),
                ('tmStruckOut', c_byte),
                ('tmPitchAndFamily', c_byte),
                ('tmCharSet', c_byte)
            ]

        class _NEWTEXTMETRIC(Structure):
            _fields_ = [
                ('tmHeight', c_long),
                ('tmAscent', c_long),
                ('tmDescent', c_long),
                ('tmInternalLeading', c_long),
                ('tmExternalLeading', c_long),
                ('tmAveCharWidth', c_long),
                ('tmMaxCharWidth', c_long),
                ('tmWeight', c_long),
                ('tmOverhang', c_long),
                ('tmDigitizedAspectX', c_long),
                ('tmDigitizedAspectY', c_long),
                ('tmFirstChar', c_wchar),  # Use unicode
                ('tmLastChar', c_wchar),
                ('tmDefaultChar', c_wchar),
                ('tmBreakChar', c_wchar),
                ('tmItalic', c_byte),
                ('tmUnderlined', c_byte),
                ('tmStruckOut', c_byte),
                ('tmPitchAndFamily', c_byte),
                ('tmCharSet', c_byte), 
                ('ntmFlags', wintypes.DWORD), 
                ('ntmSizeEM', c_uint), 
                ('ntmCellHeight', c_uint), 
                ('ntmAvgWidth', c_uint)
            ]

        # LOGFONT = _LOGFONT #xxx:
        # TEXTMETRIC = _TEXTMETRIC #xxx
        # TCHAR = c_char
        # gdi32 = WinDLL("gdi32")
        # EnumFontFamiliesEx = gdi32.EnumFontFamiliesExA
        LOGFONT = _LOGFONTW #xxx:
        TEXTMETRIC = _NEWTEXTMETRIC #xxx
        TCHAR = c_wchar
        gdi32 = WinDLL("gdi32")
        EnumFontFamiliesEx = gdi32.EnumFontFamiliesExW

        ## LPLOGFONT = POINTER(_LOGFONT) ##
        ## LPLOGFONT  is pointer of logical font structure(e.g. LOGFONT, LOGFONTW).
        ## active paramaters are lfCharSet, lfFaceName, lfPitchAndFamily==0 only
        ## http://msdn.microsoft.com/ja-jp/library/cc428521.aspx

        class _ENUMLOGFONT(Structure):
            _fields_ = [("lpelf", LOGFONT), 
                ("elfFullName", TCHAR*LF_FULLFACESIZE), 
                ("elfStyle", TCHAR*LF_FACESIZE)]
            """
            http://msdn.microsoft.com/en-us/library/windows/desktop/dd162626(v=vs.85).aspx
            typedef struct tagENUMLOGFONT {
              LOGFONT elfLogFont;
              TCHAR   elfFullName[LF_FULLFACESIZE];
              TCHAR   elfStyle[LF_FACESIZE];
            } ENUMLOGFONT, *LPENUMLOGFONT;
            """

        FONTENUMPROC = CFUNCTYPE(c_int, POINTER(_ENUMLOGFONT), POINTER(TEXTMETRIC), c_int, wintypes.LPARAM)
        EnumFontFamiliesEx.argtypes = [wintypes.HDC, POINTER(LOGFONT), FONTENUMPROC, wintypes.LPARAM, wintypes.DWORD]
        EnumFontFamiliesEx.restype = c_int

        def enum_font_families(hdc, lp_logfont, lp_enum_font_fam_ex_proc, lparam):
            #assert lp_logfont.lfPitchAndFamily.value == 0
            return EnumFontFamiliesEx(hdc, lp_logfont, lp_enum_font_fam_ex_proc, lparam, 0)

        def make_logical_font(facename="", charset=DEFAULT_CHARSET):
            # http://msdn.microsoft.com/ja-jp/library/cc428521.aspx
            #> //Arial フォントのすべてのスタイトと文字セットを列挙するには
            #> lstrcpy((LPSTR)&lf.lfFaceName, "Arial");
            #> lf.lfCharSet = DEFAULT_CHARSET;
            return LOGFONT(lfCharSet=charset, lfFaceName=facename, lfPitchAndFamily=0)


        ## function
        config.win32 = win32
        win32.pango_win32_font_map_for_display.argtypes = []
        win32.pango_win32_font_map_for_display.restype = POINTER(_PangoFontMap)

        win32.pango_win32_get_context.argtypes = []
        win32.pango_win32_get_context.restype = POINTER(_PangoContext)

        win32.pango_win32_font_map_get_font_cache.argtypes = [POINTER(_PangoFontMap)]
        win32.pango_win32_font_map_get_font_cache.restype = POINTER(_PangoWin32FontCache)

        win32.pango_win32_get_dc.argtypes = []
        win32.pango_win32_get_dc.restype = wintypes.HDC

        win32.pango_win32_shutdown_display.argtypes = []
        win32.pango_win32_shutdown_display.restype = None

        win32.pango_win32_font_cache_free.argtypes = [POINTER(_PangoWin32FontCache)]
        win32.pango_win32_font_cache_free.restype = None

        win32.pango_win32_font_description_from_logfontw.argstype = [POINTER(_LOGFONTW)]
        win32.pango_win32_font_description_from_logfontw.restype = POINTER(_PangoFontDescription)

        class WindowsNameResolver(object):
            def __init__(self, pango, gobject, win32):
                self.pango = pango
                self.gobject = gobject
                self.win32 = win32
                self.lang = None
                self.cache = None
                self.hdc = None
                self.release_targets = []

            def propose(self):
                self.fontmap = win32.pango_win32_font_map_for_display()
                self.context = win32.pango_win32_get_context()
                # self.cache = win32.pango_win32_font_map_get_font_cache(self.fontmap)
                self.hdc = win32.pango_win32_get_dc()

            def dispose(self):
                # gobject = self.gobject
                win32 = self.win32

                # gobject.g_object_unref(self.fontmap)
                # gobject.g_object_unref(self.context)
                # for target in self.release_targets:
                #     gobject.g_object_unref(target)
                self.release_targets = []
                # win32.pango_win32_font_cache_free(self.cache)
                win32.pango_win32_shutdown_display()


            def get_lookup_callback(self, ref, familyname):
                win32 = self.win32
                pango = self.pango
                def lookup_internal_family_name(lpelf, lpntm, font_type, lparam):
                    facename = lpelf.contents.lpelf.lfFaceName
                    if facename.startswith("@"):
                        return 1
                    logfontw = lpelf.contents.lpelf
                    desc = win32.pango_win32_font_description_from_logfontw(byref(logfontw))
                    ref[familyname] = pango.pango_font_description_get_family(desc)
                    return 0
                return FONTENUMPROC(lookup_internal_family_name)

            def resolve(self, familyname, lang=None, charset=SHIFTJIS_CHARSET):
                lang = lang or self.lang
                lf = make_logical_font(familyname, charset=charset)
                ref = {}
                try:
                    enum_font_families(self.hdc, byref(lf), self.get_lookup_callback(ref, familyname), c_int(0))
                except ValueError as e: #todo fix Procedure probably called with too many arguments (579920 bytes in excess)
                    pass
                return ref.get(familyname, familyname)

        return WindowsNameResolver(pango=pango, gobject=gobject, win32=win32)
