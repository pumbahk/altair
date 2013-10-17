import urllib2
import urllib
import base64

class SensibleRequest(urllib2.Request):
    def get_host(self):
        self._populate_userinfo_and_host()
        return self.host

    def get_userinfo(self):
        self._populate_userinfo_and_host()
        return self.userinfo

    def _populate_userinfo_and_host(self):
        if self.host is None or self.userinfo is None:
            userinfo_and_host, self._Request__r_host = urllib.splithost(self._Request__r_type)
            x = userinfo_and_host.split('@', 1)
            if len(x) == 1:
                x = (None, x[0])
            if x[0] is not None:
                userinfo = x[0].split(':', 1)
                if len(userinfo) == 1:
                    userinfo = (userinfo[0], None)
                else:
                    userinfo = tuple(userinfo)
            else:
                userinfo = None
            self.host = x[1]
            self.userinfo = userinfo

    def __init__(self, *args, **kwargs):
        # XXX: old style class!
        urllib2.Request.__init__(self, *args, **kwargs)
        self.userinfo = None

class BasicAuthSensibleRequest(SensibleRequest):
    def __init__(self, *args, **kwargs):
        SensibleRequest.__init__(self, *args, **kwargs)
        userinfo = self.get_userinfo()
        if userinfo is not None:
            self.add_header('Authorization', 'basic %s' % base64.b64encode(':'.join(userinfo)))
