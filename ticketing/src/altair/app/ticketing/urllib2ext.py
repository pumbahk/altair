# encoding: utf-8
import six
import urllib2
import urllib
import base64
import httplib
import socket
import ssl
import logging
from altair.httphelpers.httplib import OurHTTPSConnection

logger = logging.getLogger(__name__)

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

    def get_method(self):
        if self.method is not None:
            return self.method.upper()
        return urllib2.Request.get_method(self)

    def __init__(self, *args, **kwargs):
        # XXX: old style class!
        method = kwargs.pop('method', None)
        urllib2.Request.__init__(self, *args, **kwargs)
        self.userinfo = None
        self.method = method


class BasicAuthSensibleRequest(SensibleRequest):
    def __init__(self, *args, **kwargs):
        SensibleRequest.__init__(self, *args, **kwargs)
        userinfo = self.get_userinfo()
        if userinfo is not None:
            self.add_header('Authorization', 'basic %s' % base64.b64encode(':'.join(userinfo)))


class ClientSSLHTTPHandler(urllib2.AbstractHTTPHandler):
    def do_request_(self, request):
        host = request.get_host()
        if not host:
            raise URLError('no host given')

        if request.has_data():  # POST
            data = request.get_data()
            capitalized_content_type = 'Content-type'.capitalize()
            if request.has_header(capitalized_content_type):
                if request.get_header(capitalized_content_type) is None:
                    try:
                        del request.headers[capitalized_content_type]
                    except KeyError:
                        pass
                    try:
                        del request.unredirected_hdrs[capitalized_content_type]
                    except KeyError:
                        pass
            else:
                if self.default_content_type:
                    request.add_unredirected_header(
                        capitalized_content_type,
                        self.default_content_type)
            if not request.has_header('Content-length'):
                request.add_unredirected_header(
                    'Content-length', '%d' % len(data))

        sel_host = host
        if request.has_proxy():
            scheme, sel = splittype(request.get_selector())
            sel_host, sel_path = splithost(sel)

        if not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if not request.has_header(name):
                request.add_unredirected_header(name, value)

        return request

    http_request = do_request_
    https_request = do_request_

    def http_open(self, req):
        return self.do_open(httplib.HTTPConnection, req)

    def https_open(self, req):
        def https_connection_factory(host, **kwargs):
            return OurHTTPSConnection(
                host,
                cert_reqs=req._cert_reqs if hasattr(req, '_cert_reqs') else None,
                cert_file=req._cert_file if hasattr(req, '_cert_file') else None,
                key_file=req._key_file if hasattr(req, '_key_file') else None,
                ca_certs=req._ca_certs if hasattr(req, '_ca_certs') else None,
                ssl_version=req._ssl_version if hasattr(req, '_ssl_version') else self.ssl_version,
                **kwargs
                )
        return self.do_open(https_connection_factory, req)

    def do_open(self, http_class, req):
        host = req.get_host()
        if not host:
            raise urllib2.URLError('no host given')

        h = http_class(host, timeout=req.timeout) # will parse host:port
        h.set_debuglevel(self._debuglevel)

        headers = dict(req.unredirected_hdrs)
        headers.update(dict((k, v) for k, v in req.headers.items()
                            if k not in headers))

        headers["Connection"] = "close"
        headers = dict(
            (name.title(), val) for name, val in headers.items())

        if req._tunnel_host:
            tunnel_headers = {}
            proxy_auth_hdr = "Proxy-Authorization"
            if proxy_auth_hdr in headers:
                tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
                # Proxy-Authorization should not be sent to origin
                # server.
                del headers[proxy_auth_hdr]
            h.set_tunnel(req._tunnel_host, headers=tunnel_headers)

        try:
            h.request(req.get_method(), req.get_selector(), req.data, headers)
            try:
                r = h.getresponse(buffering=True)
            except TypeError: #buffering kw not supported
                r = h.getresponse()
        except socket.error as err: # XXX what error?
            raise urllib2.URLError(err)

        r.recv = r.read
        fp = socket._fileobject(r, close=True)

        resp = urllib2.addinfourl(fp, r.msg, req.get_full_url())
        resp.code = r.status
        resp.msg = r.reason
        return resp

    def __init__(self, *args, **kwargs):
        default_content_type = kwargs.pop('default_content_type', None)
        ssl_version = kwargs.pop('ssl_version', None)
        urllib2.AbstractHTTPHandler.__init__(self, *args, **kwargs)
        self.default_content_type = default_content_type
        self.ssl_version = ssl_version

def resolve_ssl_version(ssl_version):
    if isinstance(ssl_version, basestring):
        return getattr(ssl, 'PROTOCOL_%s' % ssl_version)
    else:
        return ssl_version

def build_opener(default_content_type='application/x-www-form-urlencoded', ssl_version=None):
    logger.debug('building opener with args: default_content_type=%s, ssl_version=%r' % (default_content_type, ssl_version))
    opener = urllib2.OpenerDirector()
    opener.add_handler(urllib2.ProxyHandler())
    opener.add_handler(urllib2.UnknownHandler())
    opener.add_handler(ClientSSLHTTPHandler(
        default_content_type=default_content_type,
        ssl_version=resolve_ssl_version(ssl_version)
        ))
    opener.add_handler(urllib2.HTTPDefaultErrorHandler())
    opener.add_handler(urllib2.HTTPRedirectHandler())
    opener.add_handler(urllib2.HTTPErrorProcessor())
    return opener

def opener_factory_from_config(config, opener_factory_key, default_opener_factory=build_opener):
    settings = config.registry.settings
    opener_factory_ref = settings.get(opener_factory_key, '').strip()
    opener_factory_args = {}
    if not opener_factory_ref:
        opener_factory_ref = default_opener_factory
        logger.info('%s is not specified; defaulting to %s and opener_factory arguments will be ignored too!' % (opener_factory_key, opener_factory_ref))
    else:
        # opener_factory が明示的に指定されたときのみ opener_factory_args を populate する
        # そうでないと、予期せぬ引数がデフォルトの opener_factory に渡されることになるため
        for k, v in six.iteritems(settings):
            if k.startswith(opener_factory_key):
                k = k[len(opener_factory_key) + 1:]
                if k:
                    opener_factory_args[k] = v
    opener_factory = config.maybe_dotted(opener_factory_ref)
    return lambda: opener_factory(**opener_factory_args) 

