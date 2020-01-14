# coding=utf-8
import os

from lxml import etree

from altair.skidata.exceptions import SkidataUnmarshalFailed
from altair.skidata.models import HSHData, Header, TSData
from altair.skidata.tests.tests import SkidataBaseTest
from altair.skidata.unmarshaller import SkidataXmlUnmarshaller


class SkidataXmlUnmarshallerTest(SkidataBaseTest):
    HSH_DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), './resources/sample_hsh_data.xml')
    HSH_DATA_WITH_ERROR_FILE_PATH = os.path.join(os.path.dirname(__file__), './resources/sample_hsh_data_with_error.xml')
    TS_DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), './resources/sample_ts_data.xml')

    def setUp(self):
        self.hsh_data_source = open(self.HSH_DATA_FILE_PATH).read()
        self.hsh_data_with_error_source = open(self.HSH_DATA_WITH_ERROR_FILE_PATH).read()
        self.ts_data_source = open(self.TS_DATA_FILE_PATH).read()

    def test_unmarshal_hsh_data(self):
        hsh_data = SkidataXmlUnmarshaller.unmarshal(self.hsh_data_source, HSHData)

        hsh_data_elem = etree.fromstring(self.hsh_data_source)
        # print(self.hsh_data_source)

        self.assert_header(hsh_data.header(), hsh_data_elem.find('Header'))
        self.assertIsNone(hsh_data.error())

    def test_unmarshal_header(self):
        hsh_data_elem = etree.fromstring(self.hsh_data_source)
        header_data_source = etree.tostring(hsh_data_elem.find('Header'))

        # Unmarshal only Header element
        header = SkidataXmlUnmarshaller.unmarshal(header_data_source, Header)

        self.assert_header(header, hsh_data_elem.find('Header'))

    def test_unmarshal_ts_data_and_existing_value_overridden(self):
        ts_data = TSData(header=Header(version='to be overridden'))

        ts_data_elem = etree.fromstring(self.ts_data_source)
        # print(self.ts_data_source)

        SkidataXmlUnmarshaller.unmarshal(self.ts_data_source, ts_data)
        self.assert_header(ts_data.header(), ts_data_elem.find('Header'))
        self.assert_ts_property(ts_data.event_ts_property(), ts_data_elem.find('TSProperty'))
        self.assert_whitelist(ts_data.whitelist(), ts_data_elem)

    def test_unmarshal_error(self):
        hsh_data = SkidataXmlUnmarshaller.unmarshal(self.hsh_data_with_error_source, HSHData)

        hsh_data_elem = etree.fromstring(self.hsh_data_with_error_source)
        # print(self.hsh_data_with_error_source)

        self.assert_header(hsh_data.header(), hsh_data_elem.find('Header'))
        self.assert_error(hsh_data.error(), hsh_data_elem.find('Error'))

    def test_raise_error_when_an_object_with_no_init_is_assigned(self):
        class NoInitClass:
            pass

        self.assertRaises(TypeError, SkidataXmlUnmarshaller.unmarshal,
                          xml_source=self.hsh_data_source, model_or_cls=NoInitClass)

    def test_raise_error_when_non_xml_data_is_assigned(self):
        self.assertRaises(SkidataUnmarshalFailed, SkidataXmlUnmarshaller.unmarshal,
                          xml_source=None, model_or_cls=HSHData)

        self.assertRaises(SkidataUnmarshalFailed, SkidataXmlUnmarshaller.unmarshal,
                          xml_source='non xml data', model_or_cls=HSHData)
