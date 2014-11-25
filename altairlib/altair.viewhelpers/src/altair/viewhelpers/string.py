import unicodedata
from cgi import escape

class RawText(object):
    def __init__(self, v):
        self.value = v

    def __html__(self):
        return self.value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value

    def __add__(self, that):
        if hasattr(that, '__html__'):
            that_html = that.__html__()
        else:
            that_html = escape(unicode(that))
        return self.__class__(self.value + that_html)

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

