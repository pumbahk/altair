# coding=utf-8
from datetime import datetime

from lxml import etree
from pyramid.testing import DummyModel

from altair.skidata.marshaller import SkidataXmlMarshaller
from altair.skidata.models import TSAction, TSData, Header, WhitelistRecord, Permission, TSProperty, TSPropertyType, \
    TSCoding
from altair.skidata.tests.tests import SkidataBaseTest


class SkidataXmlMarshallerTest(SkidataBaseTest):

    def setUp(self):
        start_date = datetime(2020, 8, 1, 12, 30, 0)

        ts_property = [
            TSProperty(type_=TSPropertyType.ORDER_NO, property_id='RE0000000001'),
            TSProperty(type_=TSPropertyType.OPEN_DATE, property_id=datetime(2019, 8, 1, 11, 0, 0)),
            TSProperty(type_=TSPropertyType.START_DATE, property_id=start_date),
            TSProperty(type_=TSPropertyType.STOCK_TYPE, property_id=u'1塁側指定席'),
            TSProperty(type_=TSPropertyType.PRODUCT_NAME, property_id=u'1塁側指定席'),
            TSProperty(type_=TSPropertyType.PRODUCT_ITEM_NAME, property_id=u'1塁側指定席'),
            TSProperty(type_=TSPropertyType.GATE, property_id='GATE A'),
            TSProperty(type_=TSPropertyType.SEAT_NAME, property_id=u'指定席'),
            TSProperty(type_=TSPropertyType.SALES_SEGMENT, property_id=u'一般発売'),
            TSProperty(type_=TSPropertyType.TICKET_TYPE, property_id=0),
            TSProperty(type_=TSPropertyType.PERSON_CATEGORY, property_id=1),
            TSProperty(type_=TSPropertyType.EVENT,
                       property_id='RE{start_date}'.format(start_date=start_date.strftime('%Y%m%d%H%M%S')))
        ]

        permission = Permission(upid=1, ts_property=ts_property)

        whitelist = WhitelistRecord(action=TSAction.INSERT, utid='TSSEJPEMBI8IH134859255TMB',
                                    coding=TSCoding.VISIBLE_QR_CODE,
                                    permission=permission, expire=datetime(2020, 8, 2, 0, 0, 0))

        header = Header(version='HSHIF25', issuer='1', receiver='1', header_id=1)

        self.ts_data = TSData(header=header, whitelist=whitelist)

    def test_marshal(self):
        xml_source = SkidataXmlMarshaller.marshal(self.ts_data, pretty_print=True)
        # print(xml_source)

        ts_data_elem = etree.fromstring(xml_source)

        self.assert_header(self.ts_data.header(), ts_data_elem.find('Header'))
        self.assert_whitelist(self.ts_data.whitelist(), ts_data_elem)

    def test_invalid_element_not_marshaled(self):
        invalid_ts_data = self.ts_data
        # Set Permission object to where WhitelistRecord is expected originally
        invalid_ts_data.set_whitelist(Permission())

        xml_source_with_no_whitelist = SkidataXmlMarshaller.marshal(invalid_ts_data, pretty_print=True)
        # print(xml_source_with_no_whitelist)

        ts_data_elem_with_no_whitelist = etree.fromstring(xml_source_with_no_whitelist)

        self.assert_header(invalid_ts_data.header(), ts_data_elem_with_no_whitelist.find('Header'))
        self.assertIsNone(ts_data_elem_with_no_whitelist.find('WhitelistRecord'))

        # Set a list of WhitelistRecord and an object with no Skidata XML context defined
        # to where WhitelistRecord is expected originally
        invalid_ts_data.set_whitelist([WhitelistRecord(), DummyModel(), WhitelistRecord(), None])
        xml_source_with_whitelist = SkidataXmlMarshaller.marshal(invalid_ts_data, pretty_print=True)
        # print(xml_source_with_whitelist)

        ts_data_elem_with_whitelist = etree.fromstring(xml_source_with_whitelist)

        self.assert_header(invalid_ts_data.header(), ts_data_elem_with_whitelist.find('Header'))
        # Assert only WhitelistRecord objects marshaled
        self.assertTrue(len(ts_data_elem_with_whitelist.findall('WhitelistRecord')) == 2)

    def test_raise_error_when_unexpected_object_is_assigned(self):
        self.assertRaises(TypeError, SkidataXmlMarshaller.marshal, model=None)
