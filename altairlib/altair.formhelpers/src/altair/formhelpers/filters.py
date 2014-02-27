# encoding: utf-8

import re
import unicodedata

def text_type_but_none_if_not_given(value):
    return unicode(value) if value is not None else None

def lstrip(chars):
    def stripper(unistr):
        return unistr and unistr.lstrip(chars)
    return stripper

def strip(chars):
    def stripper(unistr):
        return unistr and unistr.strip(chars)
    return stripper

REGEX_HYPHEN = re.compile('\-')
def strip_hyphen():
    def stripper(unistr):
        return unistr and REGEX_HYPHEN.sub('', unistr)
    return stripper

strip_spaces = strip(u' 　')

def NFKC(unistr):
    return unistr and unicodedata.normalize('NFKC', unistr)

def capitalize(unistr):
    return unistr and unistr.upper()

fullwidth_table = {
    0xff01: u'!', # ; FULLWIDTH EXCLAMATION MARK
    0xff02: u'"', # ; FULLWIDTH QUOTATION MARK
    0xff03: u'#', # ; FULLWIDTH NUMBER SIGN
    0xff04: u'$', # ; FULLWIDTH DOLLAR SIGN
    0xff05: u'%', # ; FULLWIDTH PERCENT SIGN
    0xff06: u'&', # ; FULLWIDTH AMPERSAND
    0xff07: u'\'', # ; FULLWIDTH APOSTROPHE
    0xff08: u'(', # ; FULLWIDTH LEFT PARENTHESIS
    0xff09: u')', # ; FULLWIDTH RIGHT PARENTHESIS
    0xff0a: u'*', # ; FULLWIDTH ASTERISK
    0xff0b: u'+', # ; FULLWIDTH PLUS SIGN
    0xff0c: u',', # ; FULLWIDTH COMMA
    0xff0d: u'-', # ; FULLWIDTH HYPHEN-MINUS
    0x2212: u'-', # ; MINUS SIGN
    0xff0e: u'.', # ; FULLWIDTH FULL STOP
    0xff0f: u'/', # ; FULLWIDTH SOLIDUS
    0xff1a: u':', # ; FULLWIDTH COLON
    0xff1b: u';', # ; FULLWIDTH SEMICOLON
    0xff1c: u'<', # ; FULLWIDTH LESS-THAN SIGN
    0xff1d: u'=', # ; FULLWIDTH EQUALS SIGN
    0xff1e: u'>', # ; FULLWIDTH GREATER-THAN SIGN
    0xff1f: u'?', # ; FULLWIDTH QUESTION MARK
    0xff20: u'@', # ; FULLWIDTH COMMERCIAL AT
    0xff3b: u'[', # ; FULLWIDTH LEFT SQUARE BRACKET
    0xff3c: u'\\', # ; FULLWIDTH REVERSE SOLIDUS
    0xff3d: u']', # ; FULLWIDTH RIGHT SQUARE BRACKET
    0xff3e: u'^', # ; FULLWIDTH CIRCUMFLEX ACCENT
    0xff3f: u'_', # ; FULLWIDTH LOW LINE
    0xff40: u'`', # ; FULLWIDTH GRAVE ACCENT
    0xff5b: u'{', # ; FULLWIDTH LEFT CURLY BRACKET
    0xff5c: u'|', # ; FULLWIDTH VERTICAL LINE
    0xff5d: u'}', # ; FULLWIDTH RIGHT CURLY BRACKET
    0xff5e: u'~', # ; FULLWIDTH TILDE
    0x301c: u'~', # ; WAVE DASH
    0xff5f: u'(', # ; FULLWIDTH LEFT WHITE PARENTHESIS
    0xff60: u')', # ; FULLWIDTH RIGHT WHITE PARENTHESIS
    0xffe0: u'\u00a2', # ; FULLWIDTH CENT SIGN
    0xffe1: u'\u00a3', # ; FULLWIDTH POUND SIGN
    0xffe2: u'\u00ac', # ; FULLWIDTH NOT SIGN
    0xffe3: u'\u00af', # ; FULLWIDTH MACRON
    0xffe4: u'\u00a6', # ; FULLWIDTH BROKEN BAR
    0xffe5: u'\u00a5', # ; FULLWIDTH YEN SIGN
    0xffe6: u'\u20a9', # ; FULLWIDTH WON SIGN
    }

def ignore_regexp(regexp):
    def replace(target):
        if target is None:
            return None
        return re.sub(regexp, "", target)
    return replace

ignore_space_hyphen = ignore_regexp(re.compile(u"[ \-ー　]"))

class Translate(object):
    def __init__(self, map):
        self.map = dict((ord(k) if isinstance(k, basestring) else k, v) for k, v in map.items())

    def __call__(self, unistr):
        return unistr and unistr.translate(self.map)

replace_ambiguous = Translate({
    u'\uff5e': u'\u301c',
})

def halfwidth(unistr):
    if unistr is not None:
        unistr = NFKC(unistr)
        unistr = unistr.translate(fullwidth_table)
    return unistr

def zero_as_none(data):
    return None if not data else data
