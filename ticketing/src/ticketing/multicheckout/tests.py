# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing


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
            'altair_checkout3d.auth_id': 'auth_id',
            'altair_checkout3d.auth_password': 'auth_password',
            }

        self.config.registry.settings.update(settings)

        self._callFUT(self.config)

        result = self.config.registry.utilities.lookup([], interfaces.IMultiCheckout, name="")

        self.assertEqual(result.auth_id, 'auth_id')
        self.assertEqual(result.auth_password, 'auth_password')

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
