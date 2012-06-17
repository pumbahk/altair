import unittest
import mock

class create_oauth_sigunatureTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import api
        return api.create_oauth_sigunature(*args, **kwargs)

    def test_it(self):
        oauth_consumer_key = "dpf43f3p2l4k3l03"
        oauth_token = "nnch734d00sl2jdk"
        oauth_signature_method = "HMAC-SHA1"
        oauth_timestamp = 1191242096
        oauth_nonce = "kllo9940pd9333jh"
        oauth_version = "1.0"
        form_params = [ 
            ('file', 'vacation.jpg'),
            ('size', 'original'),
        ]

        secret = 'kd94hf93k423kf44&pfkkdhi9sl3r4s00'

        method = "GET"
        url = "http://photos.example.net/photos"
        result = self._callFUT(
            method=method,
            url=url,
            oauth_consumer_key=oauth_consumer_key,
            secret=secret,
            oauth_token=oauth_token,
            oauth_signature_method=oauth_signature_method,
            oauth_timestamp=oauth_timestamp,
            oauth_nonce=oauth_nonce,
            oauth_version=oauth_version,
            form_params=form_params)

        self.assertEqual(result, "tR3+Ty81lMeYAr/Fid0kMTYa/WM=")

class create_sigunature_baseTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import api
        return api.create_signature_base(*args, **kwargs)

    def test_it(self):
        oauth_consumer_key = "dpf43f3p2l4k3l03"
        oauth_token = "nnch734d00sl2jdk"
        oauth_signature_method = "HMAC-SHA1"
        oauth_timestamp = 1191242096
        oauth_nonce = "kllo9940pd9333jh"
        oauth_version = "1.0"
        form_params = [ 
            ('file', 'vacation.jpg'),
            ('size', 'original'),
        ]

        secret = 'kd94hf93k423kf44&pfkkdhi9sl3r4s00'

        method = "GET"
        url = "http://photos.example.net/photos"
        result = self._callFUT(
            method=method,
            url=url,
            oauth_consumer_key=oauth_consumer_key,
            secret=secret,
            oauth_token=oauth_token,
            oauth_signature_method=oauth_signature_method,
            oauth_timestamp=oauth_timestamp,
            oauth_nonce=oauth_nonce,
            oauth_version=oauth_version,
            form_params=form_params)

        self.assertEqual(result, 'GET&http%3A%2F%2Fphotos.example.net%2Fphotos&file%3Dvacation.jpg%26oauth_consumer_key%3Ddpf43f3p2l4k3l03%26oauth_nonce%3Dkllo9940pd9333jh%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1191242096%26oauth_token%3Dnnch734d00sl2jdk%26oauth_version%3D1.0%26size%3Doriginal')


class RakutenOpenIDTests(unittest.TestCase):

    def _getTarget(self):
        from .api import RakutenOpenID
        return RakutenOpenID

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


#     @mock.patch('ticketing.cart.rakuten_auth.api.create_oauth_sigunature')
#     @mock.patch('urllib2.urlopen')
#     def test_get_access_token(self, mock_urlopen, mock_signature):
#         target = self._makeOne('https://api.id.rakuten.co.jp/openid/auth', 
#             'http://www.example.com/', 'akfjakldjfakldjfkalsdjfklasdjfklajdf', 'secret',
#             access_token_url='https://api.id.rakuten.co.jp/oauth',
#             )
# 
#         oauth_consumer_key = "consumer"
#         oauth_token = "token"
#         secret = "secret"
# 
#         mock_signature.return_value = "signature"
#         mock_response = mock.Mock()
#         mock_response.read.return_value = """\
# oauth_token:fafjfdjfjfsdjfslkdjflaksjd
# oauth_token_secret:fjlkjfajdfkafjalkdjfklsja"""
#         mock_urlopen.return_value = mock_response
# 
#         result = target.get_access_token(oauth_consumer_key, oauth_token, secret)
#         
#         self.assertEqual(result,
#             {"oauth_token": "fafjfdjfjfsdjfslkdjflaksjd",
#              "oauth_token_secret": "fjlkjfajdfkafjalkdjfklsja",
#             })


    @mock.patch('uuid.uuid4')
    @mock.patch('time.time')
    @mock.patch('urllib2.urlopen')
    def test_it(self, mock_urlopen, mock_time, mock_uuid):
        from mock import call

        target = self._makeOne('https://api.id.rakuten.co.jp/openid/auth', 
            'http://www.example.com/', 'akfjakldjfakldjfkalsdjfklasdjfklajdf', 'secret',
            access_token_url='https://api.id.rakuten.co.jp/oauth',
            )

        response = """\
is_valid:true
ns:http://specs.openid.net/auth/2.0"""

        mock_response = mock.Mock()
        
        mock_response.read = lambda : response
        mock_urlopen.return_value = mock_response
        mock_read = mock.Mock()
        
        mock_time.return_value = 999999999.9999
        mock_uuid.return_value = mock.Mock(hex='nonce-nonce')

        request = mock.Mock()
        identity = {
            "ns": "http://specs.openid.net/auth/2.0",
            "op_endpoint": "https://api.id.rakuten.co.jp/openid/auth",
            "claimed_id": "https://myid.rakuten.co.jp/openid/user/9Whpri7C2SulpKTnGlWg=",
            "response_nonce": "2008-09-04T04:58:20Z0",
            "mode": "id_res",
            "identity": "https://myid.rakuten.co.jp/openid/user/9Whpri7nzC2SulpKTnGlWg=",
            "return_to": "http://www.example.com/",
            "assoc_handle": "ce1b14fb7941fcd9",
            "signed": "op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle",
            "sig": "xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw=",
            "ns_ax": "",
            "ax_mode": "",
            "ax_type_nickname": "",
            "ax_value_nickname": "this-is-nickname",
            "ns_oauth": "http://specs.openid.net/extenstions/oauth/1.0",
            "oauth_request_token": "XXXXXXXXXXXXX",
            "oauth_scope": "rakutenid_basicinfo,rakutenid_contactinfo",
        }
        result = target.verify_authentication(request, identity)

        self.assertEqual(result, {"nickname": "this-is-nickname", "clamed_id": "https://myid.rakuten.co.jp/openid/user/9Whpri7C2SulpKTnGlWg="})

        self.assertEqual(mock_urlopen.mock_calls,
            [call("https://api.id.rakuten.co.jp/openid/auth?openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
                "&openid.op_endpoint=https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth"
                "&openid.claimed_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D"
                "&openid.response_nonce=2008-09-04T04%3A58%3A20Z0"
                "&openid.mode=id_res"
                "&openid.identity=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D"
                "&openid.return_to=http%3A%2F%2Fwww.example.com%2F"
                "&openid.assoc_handle=ce1b14fb7941fcd9"
                "&openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle"
                "&openid.sig=xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D"
                "&openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0"
                "&openid.oauth.request_token=XXXXXXXXXXXXX"
                "&openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo"
                "&openid.ns.ax="
                "&openid.ax.mode="
                "&openid.ax.type.nickname="
                "&openid.ax.value.nickname=this-is-nickname"
            ),
            call().close(),
            call('https://api.id.rakuten.co.jp/oauth?oauth_consumer_key=akfjakldjfakldjfkalsdjfklasdjfklajdf&oauth_token=XXXXXXXXXXXXX&oauth_signature_method=HMAC-SHA1&oauth_timestamp=999999999999&oauth_nonce=nonce-nonce&oauth_version=1.0&oauth_signature=w2sxfyOLggQ%2FtBHjVL64hS%2BKujM%3D'),
            call().close(),
        ])

    @mock.patch('uuid.uuid4')
    @mock.patch('time.time')
    @mock.patch('urllib2.urlopen')
    def test_invalid(self, mock_urlopen, mock_time, mock_uuid):
        from mock import call

        target = self._makeOne('https://api.id.rakuten.co.jp/openid/auth', 
            'http://www.example.com/', 'akfjakldjfakldjfkalsdjfklasdjfklajdf', 'secret',
            access_token_url='')

        response = """\
is_valid:false
ns:http://specs.openid.net/auth/2.0"""

        mock_response = mock.Mock()
        
        mock_response.read = lambda : response
        mock_urlopen.return_value = mock_response

        request = mock.Mock()

        mock_time.return_value = 999999999.9999
        mock_uuid.return_value = mock.Mock(hex='nonce-nonce')

        identity = {
            "ns": "http://specs.openid.net/auth/2.0",
            "op_endpoint": "https://api.id.rakuten.co.jp/openid/auth",
            "claimed_id": "https://myid.rakuten.co.jp/openid/user/9Whpri7C2SulpKTnGlWg=",
            "response_nonce": "2008-09-04T04:58:20Z0",
            "mode": "id_res",
            "identity": "https://myid.rakuten.co.jp/openid/user/9Whpri7nzC2SulpKTnGlWg=",
            "return_to": "http://www.example.com/",
            "assoc_handle": "ce1b14fb7941fcd9",
            "signed": "op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle",
            "sig": "xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw=",
            "ns_ax": "",
            "ax_mode": "",
            "ax_type_nickname": "",
            "ax_value_nickname": "this-is-nickname",
            "ns_oauth": "http://specs.openid.net/extenstions/oauth/1.0",
            "oauth_request_token": "XXXXXXXXXXXXX",
            "oauth_scope": "rakutenid_basicinfo,rakutenid_contactinfo",
        }
        result = target.verify_authentication(request, identity)

        self.assertIsNone(result)

        self.assertEqual(mock_urlopen.mock_calls, [
            call("https://api.id.rakuten.co.jp/openid/auth?openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
                "&openid.op_endpoint=https%3A%2F%2Fapi.id.rakuten.co.jp%2Fopenid%2Fauth"
                "&openid.claimed_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7C2SulpKTnGlWg%3D"
                "&openid.response_nonce=2008-09-04T04%3A58%3A20Z0"
                "&openid.mode=id_res"
                "&openid.identity=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2F9Whpri7nzC2SulpKTnGlWg%3D"
                "&openid.return_to=http%3A%2F%2Fwww.example.com%2F"
                "&openid.assoc_handle=ce1b14fb7941fcd9"
                "&openid.signed=op_endpoint%2Cclaimed_id%2Cidentity%2Creturn_to%2Cresponse_nonce%2Cassoc_handle"
                "&openid.sig=xbWVm2b4Xn4GF4O7v2opgPPrElHltmXokC1xgpjUgGw%3D"
                "&openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0"
                "&openid.oauth.request_token=XXXXXXXXXXXXX"
                "&openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo"
                "&openid.ns.ax="
                "&openid.ax.mode="
                "&openid.ax.type.nickname="
                "&openid.ax.value.nickname=this-is-nickname"
            ),
            call().close(),
            call('?oauth_consumer_key=akfjakldjfakldjfkalsdjfklasdjfklajdf&oauth_token=XXXXXXXXXXXXX&oauth_signature_method=HMAC-SHA1&oauth_timestamp=999999999999&oauth_nonce=nonce-nonce&oauth_version=1.0&oauth_signature=6ZoBYAQxl6XpQwW540ErEmDJAMc%3D'),
            call().close(),])

class parse_access_token_responseTests(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from . import api
        return api.parse_access_token_response(*args, **kwargs)

#    def test_it(self):
#        data = """\
#oauth_token:fafjfdjfjfsdjfslkdjflaksjd
#oauth_token_secret:fjlkjfajdfkafjalkdjfklsja"""
#
#        result = self._callFUT(data)
#
#        self.assertEqual(result,
#            {"oauth_token": "fafjfdjfjfsdjfslkdjflaksjd",
#             "oauth_token_secret": "fjlkjfajdfkafjalkdjfklsja",
#            })

    
class checkdigitTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .api import checkdigit
        return checkdigit(*args, **kwargs)

    def test_it(self):
        data = "4912345"
        result = self._callFUT(data)
        self.assertEqual(result, '6')

    def test_it(self):
        data = "456995111617"
        result = self._callFUT(data)
        self.assertEqual(result, '9')
