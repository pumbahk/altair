# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from .ts_core_library import *
from ctypes import wintypes
from ctypes import *
from ctypes.util import *

win32 = None
def set_win32(win32_):
    global win32
    win32 = win32_

def get_win32():
    global win32
    return win32

class _PangoWin32FontCache(Structure):
    __fields__ = [("forward", POINTER(_GHashTable)), 
                  ("back", POINTER(_GHashTable)), 
                  ("mru", POINTER(_GList)), 
                  ("mru_tail", POINTER(_GList)), 
                  ("mru_count", c_int)
    ]

## http://www.math.uiuc.edu/~gfrancis/illimath/windows/aszgard_mini/bin/MinGW/include/wingdi.h
LF_FACESIZE = 32
LF_FULLFACESIZE	= 64
DEFAULT_CHARSET	 = 1
SYMBOL_CHARSET	= 2
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

def setup_ffi(win32):
    set_win32(win32)
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
    win32.pango_win32_font_description_from_logfontw.restype = POINTER[_PangoFontDescription]


class WindowsNameResolver(object):
    def __init__(self, gobject, pango, win32):
        self.gobject = gobject
        self.pango = pango
        self.win32 = win
        self.lang = None
        self.cache = None
        self.hdc = None
        self.release_targets = []

    def using(self):
        self.propose()
        self.gobject = get_gobject()
        self.pango = get_pango()
        self.win32 = get_win32()
        yield self
        self.dispose()

    def propose(self):
        win32 = self.win32
        self.fontmap = win32.pango_win32_font_map_for_display()
        self.context = win32.pango_win32_get_context()
        self.cache = self.private.pango_win32_font_map_get_font_cache(self.fontmap)
        self.hdc = self.private.pango_win32_get_dc()

    def dispose(self):
        gobject = self.gobject
        win32 = self.win32

        gobject.g_object_unref(self.fontmap)
        gobject.g_object_unref(self.context)
        for target in self.release_targets:
            gobject.g_object_unref(target)
        self.release_targets = []
        win32.pango_win32_font_cache_free(self.cache)
        win32.pango_win32_shutdown_display()


    def get_lookup_callback(self, ref, familyname):
        win32 = self.win32
        pango = self.pango
        def lookup_internal_family_name(lpelf, lpntm, font_type, lparam):
            facename = lpelf.contents.lpelf.lfFaceName
            if facename.startswith("@"):
                return 1
            logfontw = lpelf.contents.lpelf
            desc = win32.pango_win32_font_description_from_logfontw(logfontw)
            ref[familyname] = pango.pango_font_description_get_family(desc)
            return 0
        return FONTENUMPROC(lookup_internal_family_name)

    def resolve(self, familyname, lang=None, charset=SHIFTJIS_CHARSET):
        lang = lang or self.lang
        lf = make_logical_font(familyname, charset=charset)
        ref = {}
        try:
            enum_font_families(hdc, byref(lf), self.get_lookup_callback(ref, familyname), c_int(0))
        except ValueError as e: #todo fix Procedure probably called with too many arguments (579920 bytes in excess)
            print(e)
        return ref[familyname]

