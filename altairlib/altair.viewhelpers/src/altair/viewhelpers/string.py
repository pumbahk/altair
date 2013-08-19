import unicodedata

class RawText(object):
    def __init__(self, v):
        self.value = v

    def __html__(self):
        return self.value

def truncate(s, size, ellipsis=u'...'):
    if len(s) > size:
        return s[:size] + ellipsis
    return s

def truncate_eaw(s, width, ellipsis=u'...'):
    l = 0
    c = 0
    for uch in unicode(s):
        eawcode = unicodedata.east_asian_width(uch)
        eawsize = 1 if eawcode in ('Na', 'H') else 2 # Na and H is harf-width char, otherwise full-width char.
        l += eawsize
        if l > width:
            break
        c += 1
    return truncate(s, c, ellipsis)

def nl_to_br(string, rawtext=True):
    return RawText(string.replace("\n", "<br/>"))

