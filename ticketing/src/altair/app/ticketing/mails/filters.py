import unicodedata

class Translate(object):
    def __init__(self, map):
        self.map = dict((ord(k) if isinstance(k, basestring) else k, v) for k, v in map.items())

    def __call__(self, unistr):
        return unistr and unistr.translate(self.map)

replace_ambiguous = Translate({
    u'\uff5e': u'\u301c',
})

def NFKC(unistr):
    return unicodedata.normalize('NFKC', unistr)
