#-*- coding: utf-8 -*-
import time
from unittest import TestCase
from altair.augus.protocols import ( # protocols
    VenueSyncRequest,
    VenueSyncResponse,
    PerformanceSyncRequest,
    TicketSyncRequest,
    DistributionSyncRequest,
    DistributionSyncResponse,
    PutbackRequest,
    PutbackResponse,
    PutbackFinish,
    AchievementRequest,
    AchievementResponse,
    ALL,
    )

class ProtocolTestDataFactory(object):
    protocol_args = {
        VenueSyncRequest:         {'customer_id': 1, 'venue_code': 1},
        VenueSyncResponse:        {'customer_id': 1, 'venue_code': 1},
        PerformanceSyncRequest:   {'customer_id': 1, 'event_code': 1},
        TicketSyncRequest:        {'customer_id': 1, 'event_code': 1},
        DistributionSyncRequest:  {'customer_id': 1, 'event_code': 1},
        DistributionSyncResponse: {'customer_id': 1, 'event_code': 1},
        PutbackRequest:           {'customer_id': 1, 'event_code': 1},
        PutbackResponse:          {'customer_id': 1, 'event_code': 1},
        PutbackFinish:            {'customer_id': 1, 'event_code': 1},
        AchievementRequest:       {'customer_id': 1, 'event_code': 1},
        AchievementResponse:      {'customer_id': 1, 'event_code': 1},
        }

    def create(self, _cls):
        args = self.protocol_args[_cls]
        return _cls(**args)

class FileNameTest(TestCase):
    protocol_example = {
        VenueSyncRequest: 'RT1234567KAI123456789_20130102112233.csv',
        VenueSyncResponse: 'RT1234567KAR123456789_20130102112233.csv',
        PerformanceSyncRequest: 'RT1234567GME123456789_20130102112233.csv',
        TicketSyncRequest: 'RT1234567TKT123456789_20130102112233.csv',
        DistributionSyncRequest: 'RT1234567HAI123456789_201301021122_20130102112233.csv',
        DistributionSyncResponse: 'RT1234567HAR123456789_201301021122_20130102112233.csv',
        PutbackRequest: 'RT1234567HEY123456789_201301021122_20130102112233.csv',
        PutbackResponse: 'RT1234567HEN123456789_201301021122_20130102112233.csv',
        PutbackFinish: 'RT1234567HEK123456789_201301021122_20130102112233.csv',
        AchievementRequest: 'RT1234567JIS123456789_201301021122_20130102112233.csv',
        AchievementResponse: 'RT1234567HAN123456789_201301021122_20130102112233.csv',
        }

    def test_filename_matching(self):
        factory = ProtocolTestDataFactory()
        for _cls, example in self.protocol_example.items():
            self.assert_(_cls.match_name(example),
                         '{0}: Dont match to example: {1} ({2})'\
                         .format(_cls.__name__, example, _cls.pattern))
            proto = factory.create(_cls)
            proto.set_now()
            name = ''
            try:
                name = proto.name
            except (KeyError, ValueError) as err:
                self.fail('The name formatting failed: {0}: {1}'\
                          .format(_cls.__name__, err))
            self.assert_(proto.match_name(name),
                         '{0}: Dont match to make name: {1} ({2})'\
                         .format(_cls.__name__, proto.name, _cls.pattern))

class ProtocolRecordAttributeExistTest(TestCase):
    def test_attribute_name_exist(self):
        for protocol in ALL:
            record = protocol.record
            for attribute in record.attributes:
                self.assert_(hasattr(record, attribute),
                             '{0} has no attriute: {1}'\
                             .format(record.__name__, attribute))

class ProtocolRecordAttributeMismatchTest(TestCase):
    protocol_attributes = {
        VenueSyncRequest: (
            'venue_code',
            'venue_name',
            'area_name',
            'info_name',
            'doorway_name',
            'priority',
            'floor',
            'column',
            'number',
            'block',
            'coordy',
            'coordx',
            'coordy_whole',
            'coordx_whole',
            'area_code',
            'info_code',
            'doorway_code',
            'venue_version',
            ),
        VenueSyncResponse: (
            'venue_code',
            'venue_name',
            'status',
            'venue_version',
            ),
        PerformanceSyncRequest: (
            'event_code',
            'performance_code',
            'venue_code',
            'venue_name',
            'event_name',
            'performance_name',
            'date',
            'open_on',
            'start_on',
            'venue_version',
            ),
        TicketSyncRequest: (
            'event_code',
            'performance_code',
            'venue_code',
            'seat_type_code',
            'unit_value_code',
            'seat_type_name',
            'unit_value_name',
            'seat_type_classif',
            'value',
            ),
        DistributionSyncRequest: (
            'event_code',
            'performance_code',
            'distribution_code',
            'seat_type_code',
            'unit_value_code',
            'date',
            'start_on',
            'block',
            'coordy',
            'coordx',
            'area_code',
            'info_code',
            'floor',
            'column',
            'number',
            'seat_type_classif',
            'seat_count',
            ),
        DistributionSyncResponse: (
            'event_code',
            'performance_code',
            'distribution_code',
            'status',
            ),
        PutbackRequest: (
            'event_code',
            'performance_code',
            'distribution_code',
            'seat_type_code',
            'unit_value_code',
            'date',
            'start_on',
            'block',
            'coordy',
            'coordx',
            'area_code',
            'info_code',
            'floor',
            'column',
            'number',
            'seat_type_classif',
            'seat_count',
            ),
        PutbackResponse: (
            'event_code',
            'performance_code',
            'distribution_code',
            'putback_code',
            'seat_type_code',
            'unit_value_code',
            'date',
            'start_on',
            'block',
            'coordy',
            'coordx',
            'area_code',
            'info_code',
            'floor',
            'column',
            'number',
            'seat_type_classif',
            'seat_count',
            'putback_status',
            'putback_type',
            ),
        PutbackFinish: (
            'event_code',
            'performance_code',
            'distribution_code',
            'putback_code',
            'seat_type_code',
            'unit_value_code',
            'block',
            'coordy',
            'coordx',
            'area_code',
            'info_code',
            'floor',
            'column',
            'number',
            'seat_type_classif',
            'seat_count',
            'status',
            'putback_type',
            ),
        AchievementRequest: (
            'event_code',
            'performance_code',
            'date',
            'start_on',
            'event_name',
            'performance_name',
            'venue_name',
            ),
        AchievementResponse: (
            'event_code',
            'performance_code',
            'distribution_code',
            'seat_type_code',
            'unit_value_code',
            'date',
            'start_on',
            'reservation_number',
            'block',
            'coordy',
            'coordx',
            'area_code',
            'info_code',
            'floor',
            'column',
            'number',
            'seat_type_classif',
            'seat_count',
            'unit_value',
            'processed_at',
            'achievement_status',
            ),
        }


    def test_attribute_name_mismatch(self):
        for protocol in ALL:
            testattributes = self.protocol_attributes[protocol]
            record = protocol.record
            for ii, (attr, testattr) in enumerate(
                    zip(record.attributes, testattributes), start=1):
                self.assertEqual(attr, testattr,
                                 '{0} attribute mismatch: {1} != {2} (index={3})'\
                                 .format(protocol.__name__, attr, testattr, ii))

    def test_attribute_length_mismatch(self):
        for protocol in ALL:
            testattributes = self.protocol_attributes[protocol]
            record = protocol.record
            self.assertEqual(len(record.attributes), len(testattributes),
                             "{0} 's attributes length unmatch: {1} != {2}"\
                             .format(protocol.__name__,
                                     len(record.attributes),
                                     len(testattributes)))

class ProtocolHeaderTest(TestCase):
    def test_date(self):
        for protocol_class in ALL:
            fmt = '%Y%m%d%H%M'
            proto = protocol_class()
            now = time.localtime()
            stamp = time.strftime(fmt, now)
            proto.date = stamp
            self.assertEqual(proto.date, stamp)

            proto.date = now
            self.assertEqual(proto.date, stamp)

            with self.assertRaises(ValueError):
                proto.date = None

            with self.assertRaises(ValueError):
                proto.date = 'aaaaaa'


    def test_created_at(self):
        for protocol_class in ALL:
            fmt = '%Y%m%d%H%M%S'
            proto = protocol_class()
            now = time.localtime()
            stamp = time.strftime(fmt, now)
            proto.created_at = stamp
            self.assertEqual(proto.created_at, stamp)

            proto.created_at = now
            self.assertEqual(proto.created_at, stamp)

            with self.assertRaises(ValueError):
                proto.created_at = None

            with self.assertRaises(ValueError):
                proto.created_at = 'aaaaaa'
