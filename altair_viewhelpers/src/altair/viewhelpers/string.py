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
    for c in unicode(s):
        l += unicodedata.east_asian_width(c)
        if l > width:
            break
        c += 1
    return truncate(s, c, ellipsis)

def nl_to_br(string, rawtext=True):
    return RawText(string.replace("\n", "<br/>"))

