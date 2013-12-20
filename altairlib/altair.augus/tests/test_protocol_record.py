#-*- coding: utf-8 -*-
from unittest import TestCase, skip
import string
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
from augus.types import (
    PutbackType,
    SeatTypeClassif,
    Status,
    PutbackStatus,
    AchievementStatus,
    )

DATE_TYPE, HOURMIN_TYPE, DATETIME_TYPE = range(3)

protocol_attribute_type = {
    VenueSyncRequest: (
        ('venue_code', int),
        ('venue_name', str),
        ('area_name', str),
        ('info_name', str),
        ('doorway_name', str),
        ('priority', int),
        ('floor', str),
        ('column', str),
        ('number', str),
        ('block', int),
        ('coordy', int),
        ('coordx', int),
        ('coordy_whole', int),
        ('coordx_whole', int),
        ('area_code', int),
        ('info_code', int),
        ('doorway_code', int),
        ('venue_version', int),
    ),
    VenueSyncResponse: (
        ('venue_code', int),
        ('venue_name', str),
        ('status', Status),
        ('venue_version', int),
    ),
    PerformanceSyncRequest: (
        ('event_code', int),
        ('performance_code', int),
        ('venue_code', int),
        ('venue_name', str),
        ('event_name', str),
        ('performance_name', str),
        ('date', DATE_TYPE),
        ('open_on', HOURMIN_TYPE),
        ('start_on', HOURMIN_TYPE),
        ('venue_version', int),
    ),
    TicketSyncRequest: (
        ('event_code', int),
        ('performance_code', int),
        ('venue_code', int),
        ('seat_type_code', int),
        ('unit_value_code', int),
        ('seat_type_name', str),
        ('unit_value_name', str),
        ('seat_type_classif', SeatTypeClassif),
        ('value', int),
    ),
    DistributionSyncRequest: (
        ('event_code', int),
        ('performance_code', int),
        ('distribution_code', int),
        ('seat_type_code', int),
        ('unit_value_code', int),
        ('date', DATE_TYPE),
        ('start_on', HOURMIN_TYPE),
        ('block', int),
        ('coordy', int),
        ('coordx', int),
        ('area_code', int),
        ('info_code', int),
        ('floor', str),
        ('column', str),
        ('number', str),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', int),
    ),
    DistributionSyncResponse: (
        ('event_code', int),
        ('performance_code', int),
        ('distribution_code', int),
        ('status', Status),
    ),
    PutbackRequest: (
        ('event_code', int),
        ('performance_code', int),
        ('distribution_code', int),
        ('seat_type_code', int),
        ('unit_value_code', int),
        ('date', DATE_TYPE),
        ('start_on', HOURMIN_TYPE),
        ('block', int),
        ('coordy', int),
        ('coordx', int),
        ('area_code', int),
        ('info_code', int),
        ('floor', str),
        ('column', str),
        ('number', str),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', int),
    ),
    PutbackResponse: (
        ('event_code', int),
        ('performance_code', int),
        ('distribution_code', int),
        ('putback_code', int),
        ('seat_type_code', int),
        ('unit_value_code', int),
        ('date', DATE_TYPE),
        ('start_on', HOURMIN_TYPE),
        ('block', int),
        ('coordy', int),
        ('coordx', int),
        ('area_code', int),
        ('info_code', int),
        ('floor', str),
        ('column', str),
        ('number', str),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', int),
        ('putback_status', PutbackStatus),
        ('putback_type', PutbackType),
    ),
    PutbackFinish: (
        ('event_code', int),
        ('performance_code', int),
        ('distribution_code', int),
        ('putback_code', int),
        ('seat_type_code', int),
        ('unit_value_code', int),
        ('block', int),
        ('coordy', int),
        ('coordx', int),
        ('area_code', int),
        ('info_code', int),
        ('floor', str),
        ('column', str),
        ('number', str),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', int),
        ('status', Status),
        ('putback_type', PutbackType),
    ),
    AchievementRequest: (
        ('event_code', int),
        ('performance_code', int),
        ('date', DATE_TYPE),
        ('start_on', HOURMIN_TYPE),
        ('event_name', str),
        ('performance_name', str),
        ('venue_name', str),
    ),
    AchievementResponse: (
        ('event_code', int),
        ('performance_code', int),
        ('trader_code', int),
        ('distribution_code', int),
        ('seat_type_code', int),
        ('unit_value_code', int),
        ('date', DATE_TYPE),
        ('start_on', HOURMIN_TYPE),
        ('reservation_number', str),
        ('block', int),
        ('coordy', int),
        ('coordx', int),
        ('area_code', int),
        ('info_code', int),
        ('floor', str),
        ('column', str),
        ('number', str),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', int),
        ('unit_value', int),
        ('processed_at', DATETIME_TYPE),
        ('achievement_status', AchievementStatus),
    ),
}


class ProtocolRecordAttributeMismatchTest(TestCase):
    def _generate_protocol_attributes(self):
        for protocol, attr_typ in protocol_attribute_type.items():
            testattributes = [attr for attr, typ in attr_typ]
            yield protocol, testattributes

    @skip('')
    def test_all_checked(self):
        self.fail()
        
    
    def test_attribute_name_mismatch(self):
        for protocol, testattributes in self._generate_protocol_attributes():
            record = protocol.record
            for ii, (attr, testattr) in enumerate(
                    zip(record.attributes, testattributes), start=1):
                self.assertEqual(attr, testattr,
                                 '{} attribute mismatch: {} != {} (index={})'\
                                 .format(protocol.__name__, attr, testattr, ii))
    
    def test_attribute_length_mismatch(self):
        for protocol, testattributes in self._generate_protocol_attributes():
            record = protocol.record
            self.assertEqual(len(record.attributes), len(testattributes),
                             "{} 's attributes length unmatch: {} != {}"\
                             .format(protocol.__name__,
                                     len(record.attributes),
                                     len(testattributes)))

class ProtocolRecordAttributeTypeTest(TestCase):
    def _generate_protocol_attributes(self, typ):
        for protocol, attr_typ in protocol_attribute_type.items():
            testattributes = [attr for attr, _typ in attr_typ if typ == _typ]
            yield protocol, testattributes

    def _generate_protocol_attribute(self, typ):
        for protocol, attr_typ in protocol_attribute_type.items():
            for attr in [attr for attr, _typ in attr_typ if typ == _typ]:
                yield protocol, attr

    def test_int_type(self):
        for protocol, attributes in self._generate_protocol_attributes(int):
            record = protocol.create_record()            
            for attr in attributes:
                for value in range(-100, 100):
                    input_value = str(value)
                    try:
                        setattr(record, attr, input_value)
                    except AttributeError as err:
                        raise AttributeError("can't set attribute: {}.{}"\
                                             .format(record.__class__.__name__, attr))
                    self.assertEqual(input_value, getattr(record, attr),
                                     'Type mismatch: {}.{} value={}'\
                                     .format(record.__class__.__name__,
                                             attr, repr(input_value)))
                    
            with self.assertRaises(ValueError) as err:
                setattr(record, attr, 'A')

            with self.assertRaises(TypeError) as err:
                setattr(record, attr, None)
                
    def test_str_type(self):
        japanese = map(lambda wd: wd.encode('sjis'), [u'日', u'本', u'語'])
        for protocol, attr in self._generate_protocol_attribute(str):
            record = protocol.record
            name = '{}.{}'.format(record.__name__, attr)
            rec = record()
            for ch in list(string.printable) + japanese:
                setattr(rec, attr, ch)
                rc = getattr(rec, attr)
                self.assertEqual(ch, rc,
                                 'Mismatch: {} != {} ({})'.format(
                                     repr(rc), repr(ch), name))

    def _testing_type_it(self, typ):
        """Enum Type Test Sucess Case
        """
        for protocol, attr in self._generate_protocol_attribute(typ):
            record = protocol.record
            name = '{}.{}'.format(record.__name__, attr)
            rec = record()
            
            for data in typ:
                value = data.value
                setattr(rec, attr, value)
                rc = getattr(rec, attr)
                self.assertEqual(value, rc,
                                 'Mismatch: {} != {} ({})'.format(
                                     repr(value), repr(rc), name))

        
    def test_status_type(self):
        self._testing_type_it(Status)

    @skip
    def test_date_type(self):
        self._testing_type_it(Status)

    @skip
    def test_hourmin_type(self):
        self._testing_type_it(Status)        

    def test_seat_type_classif_type(self):
        self._testing_type_it(SeatTypeClassif)        

    def test_putback_status_type(self):
        self._testing_type_it(PutbackStatus)

    def test_putback_type_type(self):
        self._testing_type_it(PutbackType)

    def test_achievement_status(self):
        self._testing_type_it(AchievementStatus)
