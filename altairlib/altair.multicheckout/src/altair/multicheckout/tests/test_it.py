# -*- coding:utf-8 -*-

import unittest
from xml.etree import ElementTree as etree
from pyramid import testing

from ..testing import DummyHTTPLib
from .. import api, models

def compare_xml(str1, str2):
    import lxml.etree as ET
    parser = ET.XMLParser(remove_blank_text=True)
    xml1 = ET.fromstring(str1, parser)
    xml2 = ET.fromstring(str2, parser)
    return ET.tostring(xml1) == ET.tostring(xml2)


class secure3d_acs_form_Tests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .. import helpers
        return helpers.secure3d_acs_form(*args, **kwargs)

    def test_it(self):

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
        """
        )


class get_multicheckout_service_Tests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        #self.session = _setup_db()

        #from altair.app.ticketing.core.models import Organization, Host
        #organization = Organization(id=1, name=u'organization_name', short_name=u'org')
        #self.session.add(organization)

        #host = Host(host_name=u'example.com', organization_id=1)
        #self.session.add(host)

        #self.session.flush()

    def tearDown(self):
        testing.tearDown()
        #_teardown_db()

    def _callFUT(self, request, *args, **kwargs):
        settings = {
            u'altair_checkout3d.base_url': u'http://example.com/api/',
            u'altair_checkout3d.timeout': '90',
        }
        self.config.registry.settings.update(settings)
        request.config = self.config
        request.altair_checkout3d_override_shop_name = u'SHOP'

        return api.get_multicheckout_service(request)

    def test_it(self):
        from ..interfaces import IMulticheckoutSettingFactory
        dummy_setting = testing.DummyResource(
            shop_name=u'SHOP',
            shop_id=1,
            auth_id=u'AUTHID',
            auth_password=u'AUTHPASS',
            )
        self.config.registry.registerUtility(
            lambda request, name: dummy_setting,
            IMulticheckoutSettingFactory,
            )
        request = testing.DummyRequest()
        service = self._callFUT(request)

        self.assertEqual(service.shop_code, 1)
        self.assertEqual(service.auth_id, u'AUTHID')
        self.assertEqual(service.auth_password, u'AUTHPASS')
        self.assertEqual(service.api_base_url, u'http://example.com/api/')


class get_pares_Tests(unittest.TestCase):
    def test_it(self):
        request = testing.DummyRequest()
        request.params = dict(PaRes='test_paras')
        self.assertEqual(api.get_pares(request), 'test_paras')


class get_md_Tests(unittest.TestCase):
    def test_it(self):
        request = testing.DummyRequest()
        request.params = dict(MD='test_md')
        self.assertEqual(api.get_md(request), 'test_md')


class sanitize_card_number_Tests(unittest.TestCase):
    def test_no_parameter(self):
        xml_data = None
        self.assertEqual(api.sanitize_card_number(xml_data), None)

    def test_secure_code(self):
        xml_data = '''
        <Message>
            <Auth>
                <Order>
                    <ItemCd>this-is-item-cd</ItemCd>
                    <ItemName>&#x5546;&#x54C1;&#x540D;</ItemName>
                    <OrderYMD>20120520</OrderYMD>
                    <SalesAmount>100</SalesAmount>
                    <TaxCarriage>50</TaxCarriage>
                    <FreeData>&#x4EFB;&#x610F;&#x9805;&#x76EE;</FreeData>
                    <ClientName>&#x697D;&#x5929;&#x592A;&#x90CE;</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </Order>
                <Card>
                    <CardNo>1111111111111111</CardNo>
                    <CardLimit>2009</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>61</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>1</SecureKind>
                </Card>
            </Auth>
        </Message>
        '''
        result = '''
        <Message>
            <Auth>
                <Order>
                    <ItemCd>this-is-item-cd</ItemCd>
                    <ItemName>&#x5546;&#x54C1;&#x540D;</ItemName>
                    <OrderYMD>20120520</OrderYMD>
                    <SalesAmount>100</SalesAmount>
                    <TaxCarriage>50</TaxCarriage>
                    <FreeData>&#x4EFB;&#x610F;&#x9805;&#x76EE;</FreeData>
                    <ClientName>&#x697D;&#x5929;&#x592A;&#x90CE;</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </Order>
                <Card>
                    <CardNo>XXXXXXXXXXXXXXXX</CardNo>
                    <CardLimit>2009</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>61</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>1</SecureKind>
                </Card>
            </Auth>
        </Message>
        '''
        self.assertTrue(compare_xml(api.sanitize_card_number(xml_data), result))

    def test_enrol(self):
        xml_data = '''
        <Message>
            <CardNumber>0123456789012345</CardNumber>
            <ExpYear>12</ExpYear>
            <ExpMonth>11</ExpMonth>
            <TotalAmount>1234567</TotalAmount>
            <Currency>392</Currency>
        </Message>
        '''
        result = '''
        <Message>
            <CardNumber>XXXXXXXXXXXXXXXX</CardNumber>
            <ExpYear>12</ExpYear>
            <ExpMonth>11</ExpMonth>
            <TotalAmount>1234567</TotalAmount>
            <Currency>392</Currency>
        </Message>
        '''
        self.assertTrue(compare_xml(api.sanitize_card_number(xml_data), result))

    def test_secure3d(self):
        xml_data = '''
        <Message>
            <Auth>
                <Order>
                    <ItemCd>this-is-item-cd</ItemCd>
                    <ItemName>&#x5546;&#x54C1;&#x540D;</ItemName>
                    <OrderYMD>20120520</OrderYMD>
                    <SalesAmount>100</SalesAmount>
                    <TaxCarriage>50</TaxCarriage>
                    <FreeData>&#x4EFB;&#x610F;&#x9805;&#x76EE;</FreeData>
                    <ClientName>&#x697D;&#x5929;&#x592A;&#x90CE;</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </Order>
                <Card>
                    <CardNo>1111111111111111</CardNo>
                    <CardLimit>2009</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>61</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>3</SecureKind>
                </Card>
                <Secure3D>
                    <Mvn>mvn</Mvn>
                    <Xid>Xid</Xid>
                    <Ts>Ts</Ts>
                    <ECI>ECI</ECI>
                    <CAVV>CAVV</CAVV>
                    <CavvAlgorithm>CavvAlgorithm</CavvAlgorithm>
                    <CardNo>1111111111111111</CardNo>
                </Secure3D>
            </Auth>
        </Message>
        '''
        result = '''
        <Message>
            <Auth>
                <Order>
                    <ItemCd>this-is-item-cd</ItemCd>
                    <ItemName>&#x5546;&#x54C1;&#x540D;</ItemName>
                    <OrderYMD>20120520</OrderYMD>
                    <SalesAmount>100</SalesAmount>
                    <TaxCarriage>50</TaxCarriage>
                    <FreeData>&#x4EFB;&#x610F;&#x9805;&#x76EE;</FreeData>
                    <ClientName>&#x697D;&#x5929;&#x592A;&#x90CE;</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </Order>
                <Card>
                    <CardNo>XXXXXXXXXXXXXXXX</CardNo>
                    <CardLimit>2009</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>61</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>3</SecureKind>
                </Card>
                <Secure3D>
                    <Mvn>mvn</Mvn>
                    <Xid>Xid</Xid>
                    <Ts>Ts</Ts>
                    <ECI>ECI</ECI>
                    <CAVV>CAVV</CAVV>
                    <CavvAlgorithm>CavvAlgorithm</CavvAlgorithm>
                    <CardNo>XXXXXXXXXXXXXXXX</CardNo>
                </Secure3D>
            </Auth>
        </Message>
        '''
        self.assertTrue(compare_xml(api.sanitize_card_number(xml_data), result))


class is_enable_secure3d_Tests(unittest.TestCase):
    def test_it(self):
        request = testing.DummyRequest()
        self.assertFalse(api.is_enable_secure3d(request, ''))
        self.assertFalse(api.is_enable_secure3d(request, '123456789012345'))
        self.assertTrue(api.is_enable_secure3d(request, '1234567890123456'))
        self.assertFalse(api.is_enable_secure3d(request, '12345678901234567'))


class Checkout3DTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        return api.Checkout3D

    def _makeOne(self, *args, **kwargs):
        # quick hack
        kwargs['api_timeout'] = kwargs.get('api_timeout', 90)
        return self._getTarget()(*args, **kwargs)

    def test_add_params(self):
        e = etree.Element('root')
        target = self._makeOne(None, None, None, None)
        result = target._add_param(e, 'param1', 'value')

        self.assertEqual(etree.tostring(result), '<param1>value</param1>')

    def test_auth_header(self):
        #auth_id, auth_password, shop_code, api_base_url
        target = self._makeOne('AUTH01', 'PASS01', 'SHOPID', 'http://example.com/')
        result = {'Authorization': 'Basic QVVUSDAxOlBBU1MwMQ=='}

        self.assertEqual(target.auth_header, result)

    def test_create_request_card_xml(self):
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

        xml_data = '''
        <Message>
            <Auth>
                <Order>
                    <ItemCd>this-is-item-cd</ItemCd>
                    <ItemName>&#x5546;&#x54C1;&#x540D;</ItemName>
                    <OrderYMD>20120520</OrderYMD>
                    <SalesAmount>100</SalesAmount>
                    <TaxCarriage>50</TaxCarriage>
                    <FreeData>&#x4EFB;&#x610F;&#x9805;&#x76EE;</FreeData>
                    <ClientName>&#x697D;&#x5929;&#x592A;&#x90CE;</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </Order>
                <Card>
                    <CardNo>1111111111111111</CardNo>
                    <CardLimit>2009</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>61</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>1</SecureKind>
                </Card>
            </Auth>
        </Message>
        '''

        self.assertTrue(compare_xml(etree.tostring(result), xml_data))

    def test_create_request_card_xml_cvv(self):
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
            SecureCode='aaaa',
            Mvn=None,
            Xid=None,
            Ts=None,
            ECI=None,
            CAVV=None,
            CavvAlgorithm=None,
        )
        result = target._create_request_card_xml(params)

        xml_data = '''
        <Message>
            <Auth>
                <Order>
                    <ItemCd>this-is-item-cd</ItemCd>
                    <ItemName>&#x5546;&#x54C1;&#x540D;</ItemName>
                    <OrderYMD>20120520</OrderYMD>
                    <SalesAmount>100</SalesAmount>
                    <TaxCarriage>50</TaxCarriage>
                    <FreeData>&#x4EFB;&#x610F;&#x9805;&#x76EE;</FreeData>
                    <ClientName>&#x697D;&#x5929;&#x592A;&#x90CE;</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </Order>
                <Card>
                    <CardNo>1111111111111111</CardNo>
                    <CardLimit>2009</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>61</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>2</SecureKind>
                </Card>
                <SecureCd>
                    <Code>aaaa</Code>
                </SecureCd>
            </Auth>
        </Message>
        '''

        self.assertTrue(compare_xml(etree.tostring(result), xml_data))

    def test_create_request_secure3d(self):
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
            Mvn='mvn',
            Xid='Xid',
            Ts='Ts',
            ECI='ECI',
            CAVV='CAVV',
            CavvAlgorithm='CavvAlgorithm',
        )
        result = target._create_request_card_xml(params)

        xml_data = '''
        <Message>
            <Auth>
                <Order>
                    <ItemCd>this-is-item-cd</ItemCd>
                    <ItemName>&#x5546;&#x54C1;&#x540D;</ItemName>
                    <OrderYMD>20120520</OrderYMD>
                    <SalesAmount>100</SalesAmount>
                    <TaxCarriage>50</TaxCarriage>
                    <FreeData>&#x4EFB;&#x610F;&#x9805;&#x76EE;</FreeData>
                    <ClientName>&#x697D;&#x5929;&#x592A;&#x90CE;</ClientName>
                    <MailAddress>ticketstar@example.com</MailAddress>
                    <MailSend>1</MailSend>
                </Order>
                <Card>
                    <CardNo>1111111111111111</CardNo>
                    <CardLimit>2009</CardLimit>
                    <CardHolderName>RAKUTEN TAROU</CardHolderName>
                    <PayKindCd>61</PayKindCd>
                    <PayCount>10</PayCount>
                    <SecureKind>3</SecureKind>
                </Card>
                <Secure3D>
                    <Mvn>mvn</Mvn>
                    <Xid>Xid</Xid>
                    <Ts>Ts</Ts>
                    <ECI>ECI</ECI>
                    <CAVV>CAVV</CAVV>
                    <CavvAlgorithm>CavvAlgorithm</CavvAlgorithm>
                    <CardNo>1111111111111111</CardNo>
                </Secure3D>
            </Auth>
        </Message>
        '''

        self.assertTrue(compare_xml(etree.tostring(result), xml_data))

    def test_create_request_card_sales_part_cancel_xml(self):
        sales_part_cancel = models.MultiCheckoutRequestCardSalesPartCancel(
            SalesAmountCancellation=200,
            TaxCarriageCancellation=10,
        )

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        result = target._create_request_card_sales_part_cancel_xml(sales_part_cancel)

        xml_data = '''<?xml version="1.0"?>
        <Message>
            <SalesPartCan>
                <Order>
                    <SalesAmountCancellation>200</SalesAmountCancellation>
                    <TaxCarriageCancellation>10</TaxCarriageCancellation>
                </Order>
            </SalesPartCan>
        </Message>
        '''

        self.assertTrue(compare_xml(etree.tostring(result), xml_data))

    def test_api_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        self.assertEqual(target.api_url, 'http://example.com/SHOP')

    def test_secure3d_enrol_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789012'
        self.assertEqual(target.secure3d_enrol_url(order_no), 'http://example.com/SHOP/3D-Secure/OrderNo/%s/Enrol' % order_no)

    def test_secure3d_auth_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789013'
        self.assertEqual(target.secure3d_auth_url(order_no), 'http://example.com/SHOP/3D-Secure/OrderNo/%s/Auth' % order_no)

    def test_card_check_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789014'
        self.assertEqual(target.card_check_url(order_no), 'http://example.com/SHOP/card/OrderNo/%s/Check' % order_no)

    def test_card_auth_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789015'
        self.assertEqual(target.card_auth_url(order_no), 'http://example.com/SHOP/card/OrderNo/%s/Auth' % order_no)

    def test_card_auth_cancel_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789016'
        self.assertEqual(target.card_auth_cancel_url(order_no), 'http://example.com/SHOP/card/OrderNo/%s/AuthCan' % order_no)

    def test_card_sales_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789017'
        self.assertEqual(target.card_sales_url(order_no), 'http://example.com/SHOP/card/OrderNo/%s/Sales' % order_no)

    def test_card_sales_part_cancel_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789018'
        self.assertEqual(target.card_sales_part_cancel_url(order_no), 'http://example.com/SHOP/card/OrderNo/%s/SalesPartCan' % order_no)

    def test_card_cancel_sales_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789018'
        self.assertEqual(target.card_cancel_sales_url(order_no), 'http://example.com/SHOP/card/OrderNo/%s/SalesCan' % order_no)

    def test_card_inquiry_url(self):
        target = self._makeOne(None, None, api_base_url="http://example.com/", shop_code="SHOP")
        order_no = '123456789019'
        self.assertEqual(target.card_inquiry_url(order_no), 'http://example.com/SHOP/card/OrderNo/%s' % order_no)

    def test_parse_response_card_xml(self):
        xml_data = """<?xml version="1.0"?>
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

        el = etree.XML(xml_data)
        result = target._parse_response_card_xml(el)

        self.assertEqual(result.__class__, models.MultiCheckoutResponseCard)
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

        self.assertEqual(result.__class__, models.MultiCheckoutInquiryResponseCard)
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
        self.assertEqual(h1.__class__, models.MultiCheckoutInquiryResponseCardHistory)
        self.assertEqual(h1.BizClassCd, "AA")
        self.assertEqual(h1.EventDate, "20120530")
        self.assertEqual(h1.SalesAmount, '9999999')
        h2 = result.histories[1]
        self.assertEqual(h2.__class__, models.MultiCheckoutInquiryResponseCardHistory)
        self.assertEqual(h2.BizClassCd, "AA")
        self.assertEqual(h2.EventDate, "20120529")
        self.assertEqual(h2.SalesAmount, '8888888')

    def test_request(self):
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
        from ..api import MultiCheckoutAPIError
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib("<Message />", status="401")
        element = etree.XML('<root />')
        try:
            target._request('http://example.com/a/b/c', element)
            self.fail("don't reach")
        except MultiCheckoutAPIError, e:
            pass

    def test_request_card_check(self):
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
        self.assertEqual(result.__class__, models.MultiCheckoutResponseCard)
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
        self.assertEqual(result.__class__, models.MultiCheckoutResponseCard)
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
        result = target.request_card_cancel_auth(order_no)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/AuthCan")
        self.assertEqual(result.__class__, models.MultiCheckoutResponseCard)
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
        order_no = "this-is-order-no"
        # params = models.MultiCheckoutRequestCard(
        #     ItemCd='this-is-item-cd',
        #     ItemName=u'商品名',
        #     OrderYMD='20120520',
        #     SalesAmount=100,
        #     TaxCarriage=50,
        #     FreeData=u'任意項目',
        #     ClientName=u'楽天太郎',
        #     MailAddress='ticketstar@example.com',
        #     MailSend='1',
        #     CardNo='1111111111111111',
        #     CardLimit='2009',
        #     CardHolderName='RAKUTEN TAROU',
        #     PayKindCd='61',
        #     PayCount='10',
        #     SecureKind='1',
        #     SecureCode=None,
        #     Mvn=None,
        #     Xid=None,
        #     Ts=None,
        #     ECI=None,
        #     CAVV=None,
        #     CavvAlgorithm=None,
        # )
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
        result = target.request_card_sales(order_no)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/Sales")
        self.assertEqual(result.__class__, models.MultiCheckoutResponseCard)
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

    def test_request_card_sales_part_cancel(self):
        order_no = "this-is-order-no"
        params = models.MultiCheckoutRequestCardSalesPartCancel(
            SalesAmountCancellation=200,
            TaxCarriageCancellation=10,
        )
        req_data = '''<?xml version="1.0"?>
        <Message>
            <SalesPartCan>
                <Order>
                    <SalesAmountCancellation>200</SalesAmountCancellation>
                    <TaxCarriageCancellation>10</TaxCarriageCancellation>
                </Order>
            </SalesPartCan>
        </Message>
        '''
        res_data = '''<?xml version="1.0"?>
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
        '''

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.request_card_sales_part_cancel(order_no, params)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/SalesPartCan")
        self.assertEqual(result.__class__, models.MultiCheckoutResponseCard)
        self.assertEqual(result.BizClassCd, "AA")
        self.assertEqual(result.Storecd, "1111111111")

    def test_request_card_cancel_sales(self):
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
        result = target.request_card_cancel_sales(order_no)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no/SalesCan")
        self.assertEqual(result.__class__, models.MultiCheckoutResponseCard)
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
        result = target.request_card_inquiry(order_no)

        self.assertEqual(target._httplib.path, "/SHOP/card/OrderNo/this-is-order-no")
        self.assertEqual(result.__class__, models.MultiCheckoutInquiryResponseCard)
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
        self.assertEqual(h1.SalesAmount, '9999999')
        h2 = result.histories[1]
        self.assertEqual(h2.BizClassCd, "AA")
        self.assertEqual(h2.EventDate, "20120529")
        self.assertEqual(h2.SalesAmount, '8888888')

    def test_parse_secure3d_enrol_response(self):
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

        self.assertEqual(result.__class__, models.Secure3DReqEnrolResponse)
        self.assertEqual(result.Md, "this-is-merchant-data")
        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.AcsUrl, "http://example.com/acs")
        self.assertEqual(result.PaReq, "this-is-pa-req")

    def test_create_secure3d_enrol_xml(self):
        enrol = models.Secure3DReqEnrolRequest(
            CardNumber="0123456789012345",
            ExpYear="12",
            ExpMonth="11",
            TotalAmount=1234567,
            Currency="392",
        )
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        result = target._create_secure3d_enrol_xml(enrol)

        xml_data = '''
        <Message>
            <CardNumber>0123456789012345</CardNumber>
            <ExpYear>12</ExpYear>
            <ExpMonth>11</ExpMonth>
            <TotalAmount>1234567</TotalAmount>
            <Currency>392</Currency>
        </Message>
        '''

        self.assertTrue(compare_xml(etree.tostring(result), xml_data))

    def test_secure3d_enrol(self):
        order_no = "this-is-order-no"
        enrol = models.Secure3DReqEnrolRequest(
            CardNumber="0123456789012345",
            ExpYear="12",
            ExpMonth="11",
            TotalAmount=1234567,
            Currency="392",
        )
        req_data = '''
        <Message>
            <CardNumber>0123456789012345</CardNumber>
            <ExpYear>12</ExpYear>
            <ExpMonth>11</ExpMonth>
            <TotalAmount>1234567</TotalAmount>
            <Currency>392</Currency>
        </Message>
        '''
        res_data = '''<?xml version="1.0"?>
        <Message>
            <Md>this-is-merchant-data</Md>
            <ErrorCd>012345</ErrorCd>
            <RetCd>0</RetCd>
            <AcsUrl>http://example.com/acs</AcsUrl>
            <PaReq>this-is-pa-req</PaReq>
        </Message>
        '''

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.secure3d_enrol(order_no, enrol)

        self.assertTrue(compare_xml(target._httplib.body, req_data))
        self.assertEqual(result.__class__, models.Secure3DReqEnrolResponse)
        self.assertEqual(result.Md, "this-is-merchant-data")
        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.AcsUrl, "http://example.com/acs")
        self.assertEqual(result.PaReq, "this-is-pa-req")

    def test_create_secure3d_auth_xml(self):
        auth = models.Secure3DAuthRequest(
            Md="this-is-md",
            PaRes="this-is-pares",
        )
        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        result = target._create_secure3d_auth_xml(auth)

        xml_data = '''
        <Message>
            <Md>this-is-md</Md>
            <PaRes>this-is-pares</PaRes>
        </Message>
        '''

        self.assertTrue(compare_xml(etree.tostring(result), xml_data))

    def test_parse_secure3d_auth_response(self):
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

        self.assertEqual(result.__class__, models.Secure3DAuthResponse)
        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.Xid, "0123456789012345678901234567")
        self.assertEqual(result.Ts, "1")
        self.assertEqual(result.Cavva, "2")
        self.assertEqual(result.Cavv, "0123456789012345678901234567")
        self.assertEqual(result.Eci, "01")
        self.assertEqual(result.Mvn, "0123456789")

    def test_secure3d_auth(self):
        order_no = "this-is-order-no"
        auth = models.Secure3DAuthRequest(
            Md="this-is-md",
            PaRes="this-is-pares",
        )
        req_data = '''
        <Message>
            <Md>this-is-md</Md>
            <PaRes>this-is-pares</PaRes>
        </Message>
        '''
        res_data = '''<?xml version="1.0"?>
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
        '''

        target = self._makeOne("user", "pass", api_base_url="http://example.com/", shop_code="SHOP")
        target._httplib = DummyHTTPLib(res_data)
        result = target.secure3d_auth(order_no, auth)

        self.assertTrue(compare_xml(target._httplib.body, req_data))
        self.assertEqual(target._httplib.path, "/SHOP/3D-Secure/OrderNo/this-is-order-no/Auth")
        self.assertEqual(result.ErrorCd, "012345")
        self.assertEqual(result.RetCd, "0")
        self.assertEqual(result.Xid, "0123456789012345678901234567")
        self.assertEqual(result.Ts, "1")
        self.assertEqual(result.Cavva, "2")
        self.assertEqual(result.Cavv, "0123456789012345678901234567")
        self.assertEqual(result.Eci, "01")
        self.assertEqual(result.Mvn, "0123456789")
