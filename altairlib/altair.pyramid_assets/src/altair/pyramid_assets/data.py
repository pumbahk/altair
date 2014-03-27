from zope.interface import implementer
from pyramid.interfaces import IAssetDescriptor
from .interfaces import IAssetResolver
from urlparse import urlparse
from cStringIO import StringIO
import re
import urllib
from base64 import b64encode, b64decode

@implementer(IAssetDescriptor)
class DataSchemeAssetDescriptor(object):
    def __init__(self, content, content_type, params, content_encoding):
        self.content = content
        self.content_type = content_type
        self.params = params
        self.content_encoding = content_encoding

    def absspec(self):
        retval = [u'data:', self.content_type]
        for k, v in self.params:
            if re.search(ur'[\s,"]', v):
                v = u'"' + v.replace(u'"', u'\\"')  + u'"'
            retval.append(u';%s=%s' % (k, v))
        if self.content_encoding == 'base64':
            retval.append(u';base64')
        retval.append(u',')
        retval.append(self.abspath())
        return u''.join(retval)

    def abspath(self):
        if self.content_encoding == 'base64':
            data = b64encode(self.content)
        else:
            data = self.content
        return urllib.quote(data)

    def stream(self):
        return StringIO(self.content)

    def isdir(self):
        return False

    def listdir(self):
        return None

    def exists(self):
        return True

@implementer(IAssetResolver)
class DataSchemeAssetResolver(object):
    def __init__(self):
        pass

    def resolve(self, spec):
        m = re.match(ur'data:(?P<content_type>[^;]+)(?P<content_type_params>(?:\s*;\s*[^,=\s]+(?:\s*=\s*(?:[^",=\s]+|"(?:[^"]+|\")*"))?)*)\s*,\s*(?P<data>.*)', spec)
        if m is None:
            raise ValueError(spec)
        params = []
        for param_pair in re.finditer(ur'\s*;\s*([^,=\s]+)(?:\s*=\s*(?:([^",=\s]+)|("(?:[^"]+|\")*")))?', m.group('content_type_params')):
            if param_pair.group(2):
                params.append((param_pair.group(1), param_pair.group(2)))
            else:
                params.append((param_pair.group(1), param_pair.group(3)[1:-1].replace('\\"', '"')))
        if len(params) > 0 and params[-1] == 'base64':
            params.pop()
            content_encoding = 'base64'
        else:
            content_encoding = None
        data = urllib.unquote(m.group('data'))
        if content_encoding == 'base64':
            content = b64decode(data)
        else:
            content = data
        content_type = m.group('content_type').strip()
        return DataSchemeAssetDescriptor(content, content_type, params, content_encoding)
