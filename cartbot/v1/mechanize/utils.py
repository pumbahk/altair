import htmlentitydefs 

__all__ = [
    'unescape_html_entities',
    'MimeType',
    ]

def unescape_html_entities(s):
    def decode_one(m):
        try:
            v = m.group(1)
            if v is not None:
                if v[0] == 'x':
                    c = int(v[1:], 16)
                else:
                    c = int(v)
            else:
                v = m.group(2)
                c = htmlentitydefs.name2codepoint[v]
            return unichr(c)
        except:
            return m.group(0)

    return re.sub(ur'&(?:#([0-9]+|x[0-9a-fA-F]+)|([a-zA-Z-]+));', decode_one, s)

class MimeType(object):
    def __init__(self, type, params):
        self.type = type
        self.params = params

    def __getitem__(self, key):
        return self.params[key]

    def get(self, key):
        return self.params.get(key)

    @classmethod
    def fromstring(cls, value):
        from email.message import Message
        m = Message()
        m['Content-Type'] = value
        params = m.get_params(header='content-type', unquote=True)
        type, _ = params.pop(0)
        return cls(type, dict(params))


