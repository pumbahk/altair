# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing

class secure3d_acs_form_Tests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import helpers
        return helpers.secure3d_acs_form(*args, **kwargs)

    def test_it(self):
        from markupsafe import Markup
        resource = testing.DummyResource(
            AcsUrl='http://www.example.com/acs',
            Md="this-is-md",
            PaReq="this-is-pa-req",
        )
        term_url = 'http://localhost/secure3d'
        request = testing.DummyRequest()

        result = self._callFUT(request, term_url, resource)

        self.assertEqual(result.__html__(),
            """<form name='PAReqForm' method='POST' action='http://www.example.com/acs'>
        <input type='hidden' name='PaReq' value='this-is-pa-req'>
        <input type='hidden' name='TermUrl' value='http://localhost/secure3d'>
        <input type='hidden' name='MD' value='this-is-md'>
        </form>
        <script type='text/javascript'>function onLoadHandler(){document.PAReqForm.submit();};window.onload = onLoadHandler; </script>
        """)

class IncludeMeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()


    def _callFUT(self, *args, **kwargs):
        from . import includeme
        return includeme(*args, **kwargs)

    def test_it(self):
        from . import interfaces
        settings = {
            'altair_checkout3d.base_url': 'http://example.com/api/',
            'altair_checkout3d.shop_id': 'this-is-shop',
            'altair_checkout3d.auth_id': 'auth_id',
            'altair_checkout3d.auth_password': 'auth_password',
            }

        self.config.registry.settings.update(settings)

        self._callFUT(self.config)

        result = self.config.registry.utilities.lookup([], interfaces.IMultiCheckout, name="")

        self.assertEqual(result.api_base_url, 'http://example.com/api/')
        self.assertEqual(result.auth_id, 'auth_id')
        self.assertEqual(result.auth_password, 'auth_password')


class get_multicheckout_service_Tests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
    def tearDown(self):
        testing.tearDown()
    def _callFUT(self, *args, **kwargs):
        from . import api
        return api.get_multicheckout_service(*args, **kwargs)

    def test_it_none(self):
        request = testing.DummyRequest()
        result = self._callFUT(request)
        self.assertIsNone(result)

    def _register_service(self):
        from . import api
        from . import interfaces
        reg = self.config.registry
        checkout3d = api.Checkout3D(None, None, None, None)
        reg.utilities.register([], interfaces.IMultiCheckout, "", checkout3d)
        return checkout3d

    def test_it(self):
        request = testing.DummyRequest()
        service = self._register_service()
        result = self._callFUT(request)
        self.assertEqual(result, service)

class secure3d_enrol_Tests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
    def tearDown(self):
        testing.tearDown()
    def _callFUT(self, *args, **kwargs):
        from . import api
        return api.secure3d_enrol(*args, **kwargs)

    def _register_service(self, httplib):
        from . import api
        from . import interfaces
        reg = self.config.registry
        auth_id = "auth"
        password = "password"
        shop_id = "shop"
        api_url = "http://api.example.com/"
        checkout3d = api.Checkout3D(auth_id, password, shop_code=shop_id, api_base_url=api_url)
        checkout3d._httplib = httplib
        reg.utilities.register([], interfaces.IMultiCheckout, "", checkout3d)
        return checkout3d

    def test_it(self):
        request = testing.DummyRequest()
        httplib = DummyHTTPLib("""<?xml version="1.0"?>
        <Message>
            <Md>this-is-merchant-data</Md>
            <ErrorCd>012345</ErrorCd>
            <RetCd>0</RetCd>
            <AcsUrl>http://example.com/acs</AcsUrl>
            <PaReq>this-is-pa-req</PaReq>
        </Message>""")
        self._register_service(httplib)
        result = self._callFUT(
            request,
            order_no="order-1",
            card_number="0123456789012345",
            exp_year="12",
            exp_month="11",
            total_amount=1234567,
        )
        self.assertEqual(result.AcsUrl, "http://example.com/acs")


class Checkout3DTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from . import api
        return api.Checkout3D

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_add_params(self):
        from xml.etree import ElementTree as etree

        e = etree.Element('root')
        target = self._makeOne(None, None, None, None)
        result = target._add_param(e, 'param1', 'value')

        self.assertEqual(etree.tostring(result), '<param1>value</param1>')

    def test_create_request_card_xml(self):
        from . import models
        target = self._makeOne(None, None, None, None)

        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='1',
            SecureCode=None,
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        result = target._create_request_card_xml(params)

    def test_create_request_card_xml_cvv(self):
        from . import models
        target = self._makeOne(None, None, None, None)

        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='2',
            SecureCode="aaaa",
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        result = target._create_request_card_xml(params)


    def test_create_request_secure3d(self):
        from . import models
        target = self._makeOne(None, None, None, None)

        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='3',
            SecureCode=None,
            Mvn="mvn",
            Xid="Xid",
            Ts="Ts",
            ECI="ECI",
            CAVV="CAVV",
            CavvAlgorithm="CavvAlgorithm",
        )
        result = target._create_request_card_xml(params)

    def test_api_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")

        self.assertEqual(target.api_url, 'http://example.com/SHOP')

    def test_parse_response_card_xml(self):
        import xml.etree.ElementTree as etree
        data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <BizClassCd>AA</BizClassCd>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <SettlementInfo>
                    <OrderNo>01234567890123456789012345678901</OrderNo>
                    <Status>012</Status>
                    <PublicTranId>0123456789012345678901</PublicTranId>
                    <AheadComCd>0123456</AheadComCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CardErrorCd>012345</CardErrorCd>
                    <ReqYmd>20120529</ReqYmd>
                    <CmnErrorCd>012345</CmnErrorCd>
                </SettlementInfo>
            </Result>
        </Message>
        """
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")

        el = etree.XML(data)
        result = target._parse_response_card_xml(el)

        self.assertEqual(result.BizClassCd, "AA")
        self.assertEqual(result.Storecd, "1111111111")
        self.assertEqual(result.OrderNo, "01234567890123456789012345678901")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.PublicTranId, "0123456789012345678901")
        self.assertEqual(result.AheadComCd, "0123456")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ReqYmd, "20120529")
        self.assertEqual(result.CmnErrorCd, "012345")

    def test_parse_inquiry_response_card_xml(self):
        import xml.etree.ElementTree as etree
        data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <Info>
                    <EventDate>20120529</EventDate>
                    <Status>012</Status>
                    <CardErrorCd>012345</CardErrorCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CmnErrorCd>012345</CmnErrorCd>
                </Info>
                <Order>
                    <OrderNo>0123456789012345678901</OrderNo>
                    <ItemName>01234567890123456789012345678901234567890123</ItemName>
                    <OrderYMD>20120530</OrderYMD>
                    <SalesAmount>7777777</SalesAmount>
                    <FreeData>NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN</FreeData>
                </Order>
                <ClientInfo>
                    <ClientName>Ticket Star</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </ClientInfo>
                <CardInfo>
                    <CardNo>XXXXXXXXXXXXXXXX</CardNo>
                    <CardLimit>1211</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>2</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>1</SecureKind>
                </CardInfo>
                <History>
                    <BizClassCd>AA</BizClassCd>
                    <EventDate>20120530</EventDate>
                    <SalesAmount>9999999</SalesAmount>
                </History>
                <History>
                    <BizClassCd>AA</BizClassCd>
                    <EventDate>20120529</EventDate>
                    <SalesAmount>8888888</SalesAmount>
                </History>
            </Result>
        </Message>
        """
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")

        el = etree.XML(data)
        result = target._parse_inquiry_response_card_xml(el)
        self.assertEqual(result.Storecd, "1111111111")

        self.assertEqual(result.EventDate, "20120529")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CmnErrorCd, "012345")

        self.assertEqual(result.OrderNo, "0123456789012345678901")
        self.assertEqual(result.ItemName, "01234567890123456789012345678901234567890123")
        self.assertEqual(result.OrderYMD, "20120530")
        self.assertEqual(result.SalesAmount, "7777777")
        self.assertEqual(result.FreeData, "NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")

        self.assertEqual(result.ClientName, "Ticket Star")
        self.assertEqual(result.MailAddress, "ticketstar@example.com")
        self.assertEqual(result.MailSend, "1")

        self.assertEqual(result.CardNo, "XXXXXXXXXXXXXXXX")
        self.assertEqual(result.CardLimit, "1211")
        self.assertEqual(result.CardHolderName, "RAKUTEN TAROU")
        self.assertEqual(result.PayKindCd, "2")
        self.assertEqual(result.PayCount, "10")
        self.assertEqual(result.SecureKind, "1")

        self.assertEqual(len(result.histories), 2)
        h1 = result.histories[0]
        self.assertEqual(h1.BizClassCd, "AA")
        self.assertEqual(h1.EventDate, "20120530")
        self.assertEqual(h1.SalesAmount, 9999999)

    def test_request(self):
        import xml.etree.ElementTree as etree
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib("<Message />")
        element = etree.XML('<root />')
        result = target._request('http://example.com/a/b/c', element)

        self.assertEqual(result.tag, 'Message')
        self.assertEqual(
            target._httplib.called,
            [
                ('HTTPConnection', ['example.com', None]),
                ('request', ['POST','/a/b/c','<root />',{
                    'Authorization': 'Basic dXNlcjpwYXNz',
                    'Content-Type': 'application/xhtml+xml;charset=UTF-8'}]),
                ('getresponse', []),
                ('read', [65536]),
                ('read', [65536]),
                ('close', [])]
        )

    def test_request_with_error(self):
        import xml.etree.ElementTree as etree
        from .api import MultiCheckoutAPIError
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib("<Message />", status="401")
        element = etree.XML('<root />')
        try:
            result = target._request('http://example.com/a/b/c', element)
            self.fail("don't reach")

        except MultiCheckoutAPIError:
            pass

    def test_request_card_check(self):
        from . import models
        order_no = "this-is-order-no"
        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='1',
            SecureCode=None,
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        res_data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <BizClassCd>AA</BizClassCd>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <SettlementInfo>
                    <OrderNo>01234567890123456789012345678901</OrderNo>
                    <Status>012</Status>
                    <PublicTranId>0123456789012345678901</PublicTranId>
                    <AheadComCd>0123456</AheadComCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CardErrorCd>012345</CardErrorCd>
                    <ReqYmd>20120529</ReqYmd>
                    <CmnErrorCd>012345</CmnErrorCd>
                </SettlementInfo>
            </Result>
        </Message>
        """

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.request_card_check(order_no, params)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/Check")
        self.assertEqual(result.BizClassCd, "AA")
        self.assertEqual(result.Storecd, "1111111111")
        self.assertEqual(result.OrderNo, "01234567890123456789012345678901")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.PublicTranId, "0123456789012345678901")
        self.assertEqual(result.AheadComCd, "0123456")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ReqYmd, "20120529")
        self.assertEqual(result.CmnErrorCd, "012345")

    def test_request_card_auth(self):
        from . import models
        order_no = "this-is-order-no"
        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='1',
            SecureCode=None,
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        res_data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <BizClassCd>AA</BizClassCd>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <SettlementInfo>
                    <OrderNo>01234567890123456789012345678901</OrderNo>
                    <Status>012</Status>
                    <PublicTranId>0123456789012345678901</PublicTranId>
                    <AheadComCd>0123456</AheadComCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CardErrorCd>012345</CardErrorCd>
                    <ReqYmd>20120529</ReqYmd>
                    <CmnErrorCd>012345</CmnErrorCd>
                </SettlementInfo>
            </Result>
        </Message>
        """

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.request_card_auth(order_no, params)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/Auth")
        self.assertEqual(result.BizClassCd, "AA")
        self.assertEqual(result.Storecd, "1111111111")
        self.assertEqual(result.OrderNo, "01234567890123456789012345678901")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.PublicTranId, "0123456789012345678901")
        self.assertEqual(result.AheadComCd, "0123456")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ReqYmd, "20120529")
        self.assertEqual(result.CmnErrorCd, "012345")

    def test_request_card_cancel_auth(self):
        from . import models
        order_no = "this-is-order-no"
        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='1',
            SecureCode=None,
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        res_data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <BizClassCd>AA</BizClassCd>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <SettlementInfo>
                    <OrderNo>01234567890123456789012345678901</OrderNo>
                    <Status>012</Status>
                    <PublicTranId>0123456789012345678901</PublicTranId>
                    <AheadComCd>0123456</AheadComCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CardErrorCd>012345</CardErrorCd>
                    <ReqYmd>20120529</ReqYmd>
                    <CmnErrorCd>012345</CmnErrorCd>
                </SettlementInfo>
            </Result>
        </Message>
        """

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.request_card_cancel_auth(order_no, params)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/AuthCan")
        self.assertEqual(result.BizClassCd, "AA")
        self.assertEqual(result.Storecd, "1111111111")
        self.assertEqual(result.OrderNo, "01234567890123456789012345678901")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.PublicTranId, "0123456789012345678901")
        self.assertEqual(result.AheadComCd, "0123456")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ReqYmd, "20120529")
        self.assertEqual(result.CmnErrorCd, "012345")

    def test_request_card_sales(self):
        from . import models
        order_no = "this-is-order-no"
        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='1',
            SecureCode=None,
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        res_data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <BizClassCd>AA</BizClassCd>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <SettlementInfo>
                    <OrderNo>01234567890123456789012345678901</OrderNo>
                    <Status>012</Status>
                    <PublicTranId>0123456789012345678901</PublicTranId>
                    <AheadComCd>0123456</AheadComCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CardErrorCd>012345</CardErrorCd>
                    <ReqYmd>20120529</ReqYmd>
                    <CmnErrorCd>012345</CmnErrorCd>
                </SettlementInfo>
            </Result>
        </Message>
        """

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.request_card_sales(order_no, params)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/Sales")
        self.assertEqual(result.BizClassCd, "AA")
        self.assertEqual(result.Storecd, "1111111111")
        self.assertEqual(result.OrderNo, "01234567890123456789012345678901")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.PublicTranId, "0123456789012345678901")
        self.assertEqual(result.AheadComCd, "0123456")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ReqYmd, "20120529")
        self.assertEqual(result.CmnErrorCd, "012345")

    def test_request_card_cancel_sales(self):
        from . import models
        order_no = "this-is-order-no"
        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='1',
            SecureCode=None,
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        res_data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <BizClassCd>AA</BizClassCd>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <SettlementInfo>
                    <OrderNo>01234567890123456789012345678901</OrderNo>
                    <Status>012</Status>
                    <PublicTranId>0123456789012345678901</PublicTranId>
                    <AheadComCd>0123456</AheadComCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CardErrorCd>012345</CardErrorCd>
                    <ReqYmd>20120529</ReqYmd>
                    <CmnErrorCd>012345</CmnErrorCd>
                </SettlementInfo>
            </Result>
        </Message>
        """

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.request_card_cancel_sales(order_no, params)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/SalesCan")
        self.assertEqual(result.BizClassCd, "AA")
        self.assertEqual(result.Storecd, "1111111111")
        self.assertEqual(result.OrderNo, "01234567890123456789012345678901")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.PublicTranId, "0123456789012345678901")
        self.assertEqual(result.AheadComCd, "0123456")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ReqYmd, "20120529")
        self.assertEqual(result.CmnErrorCd, "012345")

    def test_request_card_inquiry(self):
        from . import models
        order_no = "this-is-order-no"
        params = models.MultiCheckoutRequestCard(
            ItemCd='this-is-item-cd',
            ItemName=u'商品名',
            OrderYMD='20120520',
            SalesAmount=100,
            TaxCarriage=50,
            FreeData=u'任意項目',
            ClientName=u'楽天太郎',
            MailAddress='ticketstar@example.com',
            MailSend='1',
            CardNo='1111111111111111',
            CardLimit='2009',
            CardHolderName='RAKUTEN TAROU',
            PayKindCd='61',
            PayCount='10',
            SecureKind='1',
            SecureCode=None,
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        res_data = """<?xml version="1.0"?>
        <Message>
            <Request>
                <Storecd>1111111111</Storecd>
            </Request>
            <Result>
                <Info>
                    <EventDate>20120529</EventDate>
                    <Status>012</Status>
                    <CardErrorCd>012345</CardErrorCd>
                    <ApprovalNo>0123456</ApprovalNo>
                    <CmnErrorCd>012345</CmnErrorCd>
                </Info>
                <Order>
                    <OrderNo>0123456789012345678901</OrderNo>
                    <ItemName>01234567890123456789012345678901234567890123</ItemName>
                    <OrderYMD>20120530</OrderYMD>
                    <SalesAmount>7777777</SalesAmount>
                    <FreeData>NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN</FreeData>
                </Order>
                <ClientInfo>
                    <ClientName>Ticket Star</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </ClientInfo>
                <CardInfo>
                    <CardNo>XXXXXXXXXXXXXXXX</CardNo>
                    <CardLimit>1211</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>2</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>1</SecureKind>
                </CardInfo>
                <History>
                    <BizClassCd>AA</BizClassCd>
                    <EventDate>20120530</EventDate>
                    <SalesAmount>9999999</SalesAmount>
                </History>
                <History>
                    <BizClassCd>AA</BizClassCd>
                    <EventDate>20120529</EventDate>
                    <SalesAmount>8888888</SalesAmount>
                </History>
            </Result>
        </Message>
        """

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.request_card_inquiry(order_no, params)
        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no")

        self.assertEqual(result.Storecd, "1111111111")

        self.assertEqual(result.EventDate, "20120529")
        self.assertEqual(result.Status, "012")
        self.assertEqual(result.CardErrorCd, "012345")
        self.assertEqual(result.ApprovalNo, "0123456")
        self.assertEqual(result.CmnErrorCd, "012345")

        self.assertEqual(result.OrderNo, "0123456789012345678901")
        self.assertEqual(result.ItemName, "01234567890123456789012345678901234567890123")
        self.assertEqual(result.OrderYMD, "20120530")
        self.assertEqual(result.SalesAmount, "7777777")
        self.assertEqual(result.FreeData, "NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")

        self.assertEqual(result.ClientName, "Ticket Star")
        self.assertEqual(result.MailAddress, "ticketstar@example.com")
        self.assertEqual(result.MailSend, "1")

        self.assertEqual(result.CardNo, "XXXXXXXXXXXXXXXX")
        self.assertEqual(result.CardLimit, "1211")
        self.assertEqual(result.CardHolderName, "RAKUTEN TAROU")
        self.assertEqual(result.PayKindCd, "2")
        self.assertEqual(result.PayCount, "10")
        self.assertEqual(result.SecureKind, "1")

        self.assertEqual(len(result.histories), 2)
        h1 = result.histories[0]
        self.assertEqual(h1.BizClassCd, "AA")
        self.assertEqual(h1.EventDate, "20120530")
        self.assertEqual(h1.SalesAmount, 9999999)

    def test_parse_secure3d_enrol_response(self):
        import xml.etree.ElementTree as etree
        data = """<?xml version="1.0"?>
        <Message>
            <Md>this-is-merchant-data</Md>
            <ErrorCd>012345</ErrorCd>
            <RetCd>0</RetCd>
            <AcsUrl>http://example.com/acs</AcsUrl>
            <PaReq>this-is-pa-req</PaReq>
        </Message>
        """

        element = etree.XML(data)
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        result = target._parse_secure3d_enrol_response(element)

        self.assertEqual(result.Md, "this-is-merchant-data")
        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.AcsUrl, "http://example.com/acs")
        self.assertEqual(result.PaReq, "this-is-pa-req")

    def test_create_secure3d_enrol_xml(self):
        import xml.etree.ElementTree as etree
        from . import models as m
        enrol = m.Secure3DReqEnrolRequest(
                CardNumber="0123456789012345",
                ExpYear="12",
                ExpMonth="11",
                TotalAmount=1234567,
                Currency="392",
        )
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        result = target._create_secure3d_enrol_xml(enrol)

        self.assertEqual(etree.tostring(result),
            "<Message>"
            "<CardNumber>0123456789012345</CardNumber>"
            "<ExpYear>12</ExpYear>"
            "<ExpMonth>11</ExpMonth>"
            "<TotalAmount>1234567</TotalAmount>"
            "<Currency>392</Currency>"
            "</Message>")

    def test_secure3d_enrol(self):
        from . import models as m
        order_no = "this-is-order-no"
        enrol = m.Secure3DReqEnrolRequest(
            CardNumber="0123456789012345",
            ExpYear="12",
            ExpMonth="11",
            TotalAmount=1234567,
            Currency="392",
        )
        res_data = """<?xml version="1.0"?>
        <Message>
            <Md>this-is-merchant-data</Md>
            <ErrorCd>012345</ErrorCd>
            <RetCd>0</RetCd>
            <AcsUrl>http://example.com/acs</AcsUrl>
            <PaReq>this-is-pa-req</PaReq>
        </Message>
        """


        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)

        result = target.secure3d_enrol(order_no, enrol)

        self.assertEqual(target._httplib.body,
            "<Message>"
            "<CardNumber>0123456789012345</CardNumber>"
            "<ExpYear>12</ExpYear>"
            "<ExpMonth>11</ExpMonth>"
            "<TotalAmount>1234567</TotalAmount>"
            "<Currency>392</Currency>"
            "</Message>")
        self.assertEqual(result.Md, "this-is-merchant-data")
        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.AcsUrl, "http://example.com/acs")
        self.assertEqual(result.PaReq, "this-is-pa-req")

    def test_create_secure3d_auth_xml(self):
        import xml.etree.ElementTree as etree
        from . import models as m
        auth = m.Secure3DAuthRequest(
            Md="this-is-md",
            PaRes="this-is-pares",
        )
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        result = target._create_secure3d_auth_xml(auth)

        self.assertEqual(etree.tostring(result),
            "<Message>"
            "<Md>this-is-md</Md>"
            "<PaRes>this-is-pares</PaRes>"
            "</Message>")

    def test_parse_secure3d_auth_response(self):
        import xml.etree.ElementTree as etree
        data = """<?xml version="1.0"?>
        <Message>
        <ErrorCd>012345</ErrorCd>
        <RetCd>0</RetCd>
        <Xid>0123456789012345678901234567</Xid>
        <Ts>1</Ts>
        <Cavva>2</Cavva>
        <Cavv>0123456789012345678901234567</Cavv>
        <Eci>01</Eci>
        <Mvn>0123456789</Mvn>
        </Message>
        """

        element = etree.XML(data)
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        result = target._parse_secure3d_auth_response(element)

        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.Xid, "0123456789012345678901234567")
        self.assertEqual(result.Ts, "1")
        self.assertEqual(result.Cavva, "2")
        self.assertEqual(result.Cavv, "0123456789012345678901234567")
        self.assertEqual(result.Eci, "01")
        self.assertEqual(result.Mvn, "0123456789")

    def test_secure3d_auth(self):
        from . import models as m
        order_no = "this-is-order-no"
        auth = m.Secure3DAuthRequest(
            Md="this-is-md",
            PaRes="this-is-pares",
        )

        res_data = """<?xml version="1.0"?>
        <Message>
        <ErrorCd>012345</ErrorCd>
        <RetCd>0</RetCd>
        <Xid>0123456789012345678901234567</Xid>
        <Ts>1</Ts>
        <Cavva>2</Cavva>
        <Cavv>0123456789012345678901234567</Cavv>
        <Eci>01</Eci>
        <Mvn>0123456789</Mvn>
        </Message>
        """


        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)

        result = target.secure3d_auth(order_no, auth)

        self.assertEqual(target._httplib.body,
            "<Message>"
            "<Md>this-is-md</Md>"
            "<PaRes>this-is-pares</PaRes>"
            "</Message>")
        self.assertEqual(target._httplib.path, "/SHOP/3D-Secure/OrderNo/this-is-order-no/Auth")
        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.Xid, "0123456789012345678901234567")
        self.assertEqual(result.Ts, "1")
        self.assertEqual(result.Cavva, "2")
        self.assertEqual(result.Cavv, "0123456789012345678901234567")
        self.assertEqual(result.Eci, "01")
        self.assertEqual(result.Mvn, "0123456789")

class DummyHTTPLib(object):
    def __init__(self, response_body, status=200, reason="OK"):
        self.called = []
        self.response_body = response_body
        self.status = status
        self.reason = reason
        from io import BytesIO
        self.response_body = BytesIO(self.response_body)

    def HTTPConnection(self, host, port):
        self.host = host
        self.port = port
        self.called.append(('HTTPConnection', [host, port]))
        return self

    def HTTPSConnection(self, host, port):
        self.host = host
        self.port = port
        self.called.append(('HTTPSConnection', [host, port]))
        return self

    def request(self, method, path, body, headers):
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers
        self.called.append(('request', [method, path, body, headers]))

    def getresponse(self):
        self.called.append(('getresponse', []))
        return self

    def read(self, block=-1):
        self.called.append(('read', [block]))
        return self.response_body.read(block)

    def close(self):
        self.called.append(('close', []))
        self.response_body.close()
