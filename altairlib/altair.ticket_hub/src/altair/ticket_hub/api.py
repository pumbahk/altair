# -*- coding: utf-8 -*-

import logging
import base64
import xmltodict
from urllib2 import Request, urlopen
from datetime import datetime
from Crypto.Cipher import AES
from zope.interface import implementer
from http.facility import TicketHubFacilityRequest
from http.health import TicketHubHealthRequest
from http.item_group import TicketHubItemGroupRequest
from http.item import TicketHubItemListRequest
from http.cart import TicketHubCreateCartRequest, TicketHubGetCartRequest
from http.order import TicketHubCreateTempOrderRequest, TicketHubCompleteTempOrderRequest
from .interfaces import ITicketHubAPI
from .exc import TicketHubAPIError

logger = logging.getLogger(__name__)

# TODO: get from setting file
tickethub_base_uri = 'https://stg.webket.jp/tickethub/v9' # prod 'https://tickethub.webket.jp/'
seller_code = '06006' # 事業者コード
seller_channel_code = '0011' # 事業者チャネルコード
api_key = 'lQ1SDy' # 認証キー
api_secret = 'Cpy*t^6^d}b' # パスワード

"""
X-Lang-Code: 0:日本語、1:英語、2:中国簡体、3:中国繁体
"""
JA_JP = 0
EN_US = 1
ZH_CN = 2
ZH_TW = 3

class TicketHubEncryptor(object):
    def __init__(self, secret, block_size=16):
        self.secret = secret.ljust(block_size,chr(0))
        self.bs = block_size

    def encrypt(self, raw):
        cipher = AES.new(self.secret, AES.MODE_ECB)
        padded = self._pad(raw)
        enc = cipher.encrypt(padded)
        return base64.b64encode(enc)

    def _pad(self, s):
        number_of_bytes_to_pad = self.bs - len(s) % self.bs
        ascii_string = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plain_text = s + padding_str
        return padded_plain_text

class TicketHubClient(object):
    def __init__(self, base_uri, api_key, api_secret, seller_code, seller_channel_code):
        self.base_uri = base_uri
        self.api_key = api_key
        self.seller_code = seller_code
        self.seller_channel_code = seller_channel_code
        self.encryptor = TicketHubEncryptor(api_secret)

    def send(self, request):
        req = self._build_request(request)
        try:
            raw_res = urlopen(req)
            response = request.build_response(raw_res.read())
        except Exception as e:
            raise TicketHubAPIError(e.message)
        return response

    def _build_auth_key(self, requested_at=datetime.now()):
        date_str = requested_at.strftime('%Y%m%d')
        base = self.api_key + date_str + self.seller_code
        evens = base[1::2] #偶数indexの文字集合
        odds = base[::2] #奇数indexの文字集合
        difficult = evens + odds if int(date_str) % 2 == 0 else odds + evens # 難読化
        return self.encryptor.encrypt(difficult).strip('=')

    def _build_url(self, path):
        return self.base_uri + path

    def _build_request(self, ticket_hub_reqeust):
        url = self._build_url(ticket_hub_reqeust.path())
        request_dict = ticket_hub_reqeust.params()
        method = ticket_hub_reqeust.method
        data = xmltodict.unparse(request_dict) if request_dict else None
        req = Request(url, data=data)
        req.get_method = lambda: method
        req.add_header(u'Content-Type', 'application/xml')
        req.add_header(u'X-Auth-Key', self._build_auth_key())
        req.add_header(u'X-Seller-Code', self.seller_code)
        req.add_header(u'X-Seller-Channel-Code', self.seller_channel_code)
        req.add_header(u'X-Lang-Code', JA_JP)
        return req

@implementer(ITicketHubAPI)
class TicketHubAPI(object):
    def __init__(self, client):
        self.client = client

    def healths(self):
        req = TicketHubHealthRequest()
        return self.client.send(req)

    def facility(self, id):
        return self.client.send(TicketHubFacilityRequest(id))

    def item_groups(self, facility_code, agent_code):
        return self.client.send(TicketHubItemGroupRequest(facility_code, agent_code))

    def items(self, facility_code, agent_code, item_group_code):
        return self.client.send(TicketHubItemListRequest(facility_code, agent_code, item_group_code))

    def create_cart(self, facility_code, agent_code, cart_items):
        return self.client.send(
            TicketHubCreateCartRequest(facility_code, agent_code, cart_items)
        )

    def cart(self, cart_id):
        return self.client.send(
            TicketHubGetCartRequest(cart_id)
        )

    def create_temp_order(self, tickethub_cart_id):
        return self.client.send(TicketHubCreateTempOrderRequest(tickethub_cart_id))

    def complete_order(self, tickethub_order_no):
        return self.client.send(TicketHubCompleteTempOrderRequest(tickethub_order_no))
