import unittest
import webtest

def app(environ, start_response):
    from . import browser
    start_response('200 OK',
                   [('Content-type', 'text/plain')])
    body = u"environ browserid = %s" % environ['repoze.browserid']
    body += u" local browserid = %s" % browser.id
    body = body.encode('utf-8')
    return [body]

class BrowserIDMiddlewareTests(unittest.TestCase):


    def _getTarget(self):
        from . import BrowserIDMiddleware
        return BrowserIDMiddleware

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_none(self):
        target = self._makeOne(app, cookie_name='browserid', env_key='repoze.browserid')

        testapp = webtest.TestApp(target)

        result = testapp.get('/')
        
        self.assertEqual(result.body, 'environ browserid = None local browserid = None')

    def test_it(self):
        target = self._makeOne(app, cookie_name='browserid', env_key='repoze.browserid')


        testapp = webtest.TestApp(target)
        testapp.cookies['browserid'] = 'this-is-browser-id'

        result = testapp.get('/')

        self.assertEqual(result.body, 'environ browserid = this-is-browser-id local browserid = this-is-browser-id')
