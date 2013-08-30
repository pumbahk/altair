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

def zero_as_none(data):
    return None if not data else data
