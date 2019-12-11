import unittest
from datetime import datetime, date, time

from altair.skidata.models import Permission, TSProperty, TSAction, TSCoding, HSHErrorNumber, WhitelistRecord, \
    TSPropertyType, HSHErrorType, Arguments, EventTSProperty
from altair.skidata.utils import ALLOWED_ITERABLE_TYPES


class SkidataBaseTest(unittest.TestCase):
    def assert_header(self, header, header_elem):
        self.assertEqual(header.version(), header_elem.find('Version').text)
        self.assertEqual(header.issuer(), header_elem.find('Issuer').text)
        self.assertEqual(header.receiver(), header_elem.find('Receiver').text)

        # ID Element is not mandatory
        header_id = header.header_id()
        if isinstance(header_id, (int, long)):
            self.assertEqual(str(header_id), header_elem.find('ID').text)

    @staticmethod
    def _make_tuple(list_):
        return tuple(list(ALLOWED_ITERABLE_TYPES) + list_)

    def assert_error(self, error, error_elem):
        e_type = error.type()
        if isinstance(e_type, HSHErrorType):
            e_type = e_type.value
        self.assertEqual(e_type, error_elem.get('Type'))

        number = error.number()
        if isinstance(number, HSHErrorNumber):
            number = number.value
        self.assertEqual(number, int(error_elem.find('Number').text))

        self.assertEqual(error.description(), error_elem.find('Description').text)

        # EventTSProperty element is not mandatory
        event_ts_property = error.event_ts_property()
        if isinstance(event_ts_property, EventTSProperty):
            self.assert_ts_property(event_ts_property, error_elem.find('TSProperty'))
        elif event_ts_property is not None:
            self.fail(u'{} is not {} object'.format(event_ts_property, EventTSProperty.__name__))

        # WhitelistRecord element is not mandatory
        whitelist = error.whitelist()
        if isinstance(whitelist, self._make_tuple([WhitelistRecord])):
            self.assert_whitelist(whitelist, error_elem)
        elif whitelist is not None:
            self.fail(u'{} is not an iterable or {} object'.format(whitelist, WhitelistRecord.__name__))

    def assert_whitelist(self, whitelist, ts_data_or_error_elem):
        for w in whitelist if isinstance(whitelist, ALLOWED_ITERABLE_TYPES) else [whitelist]:
            w_elem = self.find_whitelist_elem(w.utid(), ts_data_or_error_elem)

            action = w.action()
            if isinstance(action, TSAction):
                action = action.value
            self.assertEqual(action, w_elem.find('Action').text)

            self.assertEqual(w.utid(), w_elem.find('UTID').text)

            coding = w.coding()
            if isinstance(coding, TSCoding):
                coding = str(coding.value)
            elif isinstance(coding, (int, long)):
                coding = str(coding)
            self.assertEqual(coding, w_elem.find('Coding').text)

            # Expire attribute is not mandatory
            expire = w.expire()
            if expire is not None:
                if isinstance(expire, datetime):
                    expire = expire.isoformat()
                self.assertEqual(expire, w_elem.get('Expire'))

            # Permission element is not mandatory
            permission = w.permission()
            if isinstance(permission, self._make_tuple([Permission])):
                self.assert_permission(permission, w_elem)
            elif permission is not None:
                self.fail(u'{} is not an iterable or {} object'.format(permission, Permission.__name__))

    def assert_permission(self, permission, whitelist_elem):
        for p in permission if isinstance(permission, ALLOWED_ITERABLE_TYPES) else [permission]:
            p_elem = self.find_permission_elem(p.upid(), whitelist_elem)

            # TSProperty element is not mandatory
            ts_property = p.ts_property()
            if isinstance(ts_property, self._make_tuple([TSProperty])):
                self.assert_ts_option(ts_property, p_elem)
            elif ts_property is not None:
                self.fail(u'{} is not an iterable or {} object'.format(ts_property, TSProperty.__name__))

    def assert_ts_property(self, ts_property, ts_property_elem):
        type_ = ts_property.type()
        if isinstance(type_, TSPropertyType):
            type_ = type_.value
        self.assertEqual(type_, ts_property_elem.get('Type'))

        property_id = unicode(ts_property.property_id())
        self.assertEqual(property_id, ts_property_elem.find('ID').text)

        # Expire attribute is not mandatory
        expire = ts_property.expire()
        if expire is not None:
            if isinstance(expire, datetime):
                expire = expire.isoformat()
            self.assertEqual(expire, ts_property_elem.get('Expire'))

        if not isinstance(ts_property, EventTSProperty):
            return

        # Action element is not mandatory
        action = ts_property.action()
        if action is not None:
            if isinstance(action, TSAction):
                action = action.value
            self.assertEqual(action, ts_property_elem.find('Action').text)

        # Name element is not mandatory
        name = ts_property.name()
        if name is not None:
            self.assertEqual(name, ts_property_elem.find('Name').text)

        # Arguments element is not mandatory
        arguments = ts_property.arguments()
        if isinstance(arguments, Arguments):
            self.assert_arguments(arguments, ts_property_elem.find('Arguments'))
        elif arguments is not None:
            self.fail(u'{} is not or {} object'.format(arguments, Arguments.__name__))

    def assert_arguments(self, arguments, arguments_elem):
        place = arguments.place()
        if place is not None:
            self.assertEqual(place, arguments_elem.find('Place').text)

        from_date = arguments.from_date()
        if isinstance(from_date, date):
            self.assertEqual(from_date.isoformat(), arguments_elem.find('FromDate').text)

        from_time = arguments.from_time()
        if isinstance(from_date, time):
            self.assertEqual(from_time.strftime('%H:%M'), arguments_elem.find('FromTime').text)

        to_date = arguments.to_date()
        if isinstance(to_date, date):
            self.assertEqual(to_date.isoformat(), arguments_elem.find('ToDate').text)

        to_time = arguments.to_time()
        if isinstance(to_time, time):
            self.assertEqual(to_time.strftime('%H:%M'), arguments_elem.find('ToTime').text)

    def assert_ts_option(self, ts_property, permission_elem):
        for t in ts_property if isinstance(ts_property, ALLOWED_ITERABLE_TYPES) else [ts_property]:
            type_ = t.type()
            if isinstance(type_, TSPropertyType):
                type_ = type_.value
            t_elem = self.find_ts_property_elem(type_, permission_elem)

            property_id = unicode(t.property_id())
            self.assertEqual(property_id, t_elem.find('ID').text)

    def find_whitelist_elem(self, utid, hsh_data):
        for whitelist_elem in hsh_data.findall('WhitelistRecord'):
            if utid == whitelist_elem.find('UTID').text:
                return whitelist_elem
        self.fail('No WhitelistRecord element with UTID set to {} found in {}'.format(utid, hsh_data))

    def find_permission_elem(self, upid, whitelist_elem):
        for permission_elem in whitelist_elem.findall('Permission'):
            if str(upid) == permission_elem.find('UPID').text:
                return permission_elem
        self.fail('No Permission element with UPID set to {} found in {}'.format(upid, whitelist_elem))

    def find_ts_property_elem(self, type_, permission_elem):
        for ts_property_elem in permission_elem.findall('TSProperty'):
            if type_ == ts_property_elem.get('Type'):
                return ts_property_elem
        self.fail('No TSProperty element with Type set to {} found in {}'.format(type_, permission_elem))
