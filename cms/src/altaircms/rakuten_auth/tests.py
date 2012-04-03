import unittest
import mock

class RakutenOpenIDTests(unittest.TestCase):

    def _getTarget(self):
        from .api import RakutenOpenID
        return RakutenOpenID

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch('urllib2.urlopen')
    def test_it(self, mock_urlopen):

        target = self._makeOne('https://api.id.rakuten.co.jp/openid/auth', 'http://www.example.com/', 'akfjakldjfakldjfkalsdjfklasdjfklajdf')

        response = """\
is_valid:true
ns:http://specs.openid.net/auth/2.0"""

        mock_response = mock.Mock()
        
        mock_response.read = lambda : response
        mock_urlopen.return_value = mock_response
        mock_read = mock.Mock()
        
        request = mock.Mock()
        request.GET = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.op_endpoint": "https://api.id.rakuten.co.jp/openid/auth",
            "openid.claimed_id": "https://myid.rakuten.co.jp/openid/user/9Whpri7C2SulpKTnGlWg=",
            "openid.response_nonce": "2008-09-04T04:58:20Z0",
            "openid.mode": "id_res",
            "openid.identity": "https://myid.rakuten.co.jp/openid/user/9Whpri7nzC2SulpKTnGlWg=",
            "openid.return_to": "http://www.example.com/",
            "openid.assoc_handle": "ce1b14fb7941fcd9",
            "openid.signed": "op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle",
            "openid.sig": "xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw=",
            "openid.ns.oauth": "http://specs.openid.net/extenstions/oauth/1.0",
            "openid.oauth.request_token": "XXXXXXXXXXXXX",
            "openid.oauth.scope": "rakutenid_basicinfo,rakutenid_contactinfo",
        }
        result = target.verify_authentication(request)

        self.assertEqual(result, "https://myid.rakuten.co.jp/openid/user/9Whpri7C2SulpKTnGlWg=")

        mock_urlopen.assert_called_with("https://api.id.rakuten.co.jp/openid/auth?openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
            "&openid.op_endpoint=https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth"
            "&openid.claimed_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D"
            "&openid.response_nonce=2008-09-04T04%3A58%3A20Z0"
            "&openid.mode=check_authentication"
            "&openid.identity=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D"
            "&openid.return_to=http%3A%2F%2Fwww.example.com%2F"
            "&openid.assoc_handle=ce1b14fb7941fcd9"
            "&openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle"
            "&openid.sig=xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D"
            "&openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0"
            "&openid.oauth.request_token=XXXXXXXXXXXXX"
            "&openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo")

    @mock.patch('urllib2.urlopen')
    def test_invalid(self, mock_urlopen):

        target = self._makeOne('https://api.id.rakuten.co.jp/openid/auth', 'http://www.example.com/', 'akfjakldjfakldjfkalsdjfklasdjfklajdf')

        response = """\
is_valid:false
ns:http://specs.openid.net/auth/2.0"""

        mock_response = mock.Mock()
        
        mock_response.read = lambda : response
        mock_urlopen.return_value = mock_response

        request = mock.Mock()
        request.GET = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.op_endpoint": "https://api.id.rakuten.co.jp/openid/auth",
            "openid.claimed_id": "https://myid.rakuten.co.jp/openid/user/9Whpri7C2SulpKTnGlWg=",
            "openid.response_nonce": "2008-09-04T04:58:20Z0",
            "openid.mode": "id_res",
            "openid.identity": "https://myid.rakuten.co.jp/openid/user/9Whpri7nzC2SulpKTnGlWg=",
            "openid.return_to": "http://www.example.com/",
            "openid.assoc_handle": "ce1b14fb7941fcd9",
            "openid.signed": "op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle",
            "openid.sig": "xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw=",
            "openid.ns.oauth": "http://specs.openid.net/extenstions/oauth/1.0",
            "openid.oauth.request_token": "XXXXXXXXXXXXX",
            "openid.oauth.scope": "rakutenid_basicinfo,rakutenid_contactinfo",
        }
        result = target.verify_authentication(request)

        self.assertIsNone(result)

        mock_urlopen.assert_called_with("https://api.id.rakuten.co.jp/openid/auth?openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
            "&openid.op_endpoint=https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth"
            "&openid.claimed_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D"
            "&openid.response_nonce=2008-09-04T04%3A58%3A20Z0"
            "&openid.mode=check_authentication"
            "&openid.identity=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D"
            "&openid.return_to=http%3A%2F%2Fwww.example.com%2F"
            "&openid.assoc_handle=ce1b14fb7941fcd9"
            "&openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle"
            "&openid.sig=xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D"
            "&openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0"
            "&openid.oauth.request_token=XXXXXXXXXXXXX"
            "&openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo")
