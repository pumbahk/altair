#-*- coding: utf-8 -*-
from unittest import TestCase, skip
import string
from altair.augus.errors import ProtocolFormatError
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
from altair.augus.types import (
    NumberType,
    StringType,
    DateType,
    HourMinType,
    DateTimeType,
    PutbackType,
    SeatTypeClassif,
    Status,
    PutbackStatus,
    AchievementStatus,
    )



protocol_attribute_type = {
    VenueSyncRequest: (
        ('venue_code', NumberType),
        ('venue_name', StringType),
        ('area_name', StringType),
        ('info_name', StringType),
        ('doorway_name', StringType),
        ('priority', NumberType),
        ('floor', StringType),
        ('column', StringType),
        ('number', StringType),
        ('block', NumberType),
        ('coordy', NumberType),
        ('coordx', NumberType),
        ('coordy_whole', NumberType),
        ('coordx_whole', NumberType),
        ('area_code', NumberType),
        ('info_code', NumberType),
        ('doorway_code', NumberType),
        ('venue_version', NumberType),
    ),
    VenueSyncResponse: (
        ('venue_code', NumberType),
        ('venue_name', StringType),
        ('status', Status),
        ('venue_version', NumberType),
    ),
    PerformanceSyncRequest: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('venue_code', NumberType),
        ('venue_name', StringType),
        ('event_name', StringType),
        ('performance_name', StringType),
        ('date', DateType),
        ('open_on', HourMinType),
        ('start_on', HourMinType),
        ('venue_version', NumberType),
    ),
    TicketSyncRequest: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('venue_code', NumberType),
        ('seat_type_code', NumberType),
        ('unit_value_code', NumberType),
        ('seat_type_name', StringType),
        ('unit_value_name', StringType),
        ('seat_type_classif', SeatTypeClassif),
        ('value', NumberType),
    ),
    DistributionSyncRequest: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('distribution_code', NumberType),
        ('seat_type_code', NumberType),
        ('unit_value_code', NumberType),
        ('date', DateType),
        ('start_on', HourMinType),
        ('block', NumberType),
        ('coordy', NumberType),
        ('coordx', NumberType),
        ('area_code', NumberType),
        ('info_code', NumberType),
        ('floor', StringType),
        ('column', StringType),
        ('number', StringType),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', NumberType),
    ),
    DistributionSyncResponse: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('distribution_code', NumberType),
        ('status', Status),
    ),
    PutbackRequest: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('distribution_code', NumberType),
        ('seat_type_code', NumberType),
        ('unit_value_code', NumberType),
        ('date', DateType),
        ('start_on', HourMinType),
        ('block', NumberType),
        ('coordy', NumberType),
        ('coordx', NumberType),
        ('area_code', NumberType),
        ('info_code', NumberType),
        ('floor', StringType),
        ('column', StringType),
        ('number', StringType),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', NumberType),
    ),
    PutbackResponse: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('distribution_code', NumberType),
        ('putback_code', NumberType),
        ('seat_type_code', NumberType),
        ('unit_value_code', NumberType),
        ('date', DateType),
        ('start_on', HourMinType),
        ('block', NumberType),
        ('coordy', NumberType),
        ('coordx', NumberType),
        ('area_code', NumberType),
        ('info_code', NumberType),
        ('floor', str),
        ('column', StringType),
        ('number', StringType),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', NumberType),
        ('putback_status', PutbackStatus),
        ('putback_type', PutbackType),
    ),
    PutbackFinish: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('distribution_code', NumberType),
        ('putback_code', NumberType),
        ('seat_type_code', NumberType),
        ('unit_value_code', NumberType),
        ('block', NumberType),
        ('coordy', NumberType),
        ('coordx', NumberType),
        ('area_code', NumberType),
        ('info_code', NumberType),
        ('floor', StringType),
        ('column', StringType),
        ('number', StringType),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', NumberType),
        ('status', Status),
        ('putback_type', PutbackType),
    ),
    AchievementRequest: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('date', DateType),
        ('start_on', HourMinType),
        ('event_name', StringType),
        ('performance_name', StringType),
        ('venue_name', StringType),
    ),
    AchievementResponse: (
        ('event_code', NumberType),
        ('performance_code', NumberType),
        ('trader_code', NumberType),
        ('distribution_code', NumberType),
        ('seat_type_code', NumberType),
        ('unit_value_code', NumberType),
        ('date', DateType),
        ('start_on', HourMinType),
        ('reservation_number', StringType),
        ('block', NumberType),
        ('coordy', NumberType),
        ('coordx', NumberType),
        ('area_code', NumberType),
        ('info_code', NumberType),
        ('floor', StringType),
        ('column', StringType),
        ('number', StringType),
        ('seat_type_classif', SeatTypeClassif),
        ('seat_count', NumberType),
        ('unit_value', NumberType),
        ('processed_at', DateTimeType),
        ('achievement_status', AchievementStatus),
    ),
}


class IllegalRecordTest(TestCase):
    def test_illegal_record_load_test(self):
        for protocol in ALL:
            record = protocol.record()
            with self.assertRaises(ProtocolFormatError):
                record.load([])

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

    def test_number_type(self):
        for protocol, attributes in self._generate_protocol_attributes(NumberType):
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
        japanese = [u'日', u'本', u'語']
        for protocol, attr in self._generate_protocol_attribute(StringType):
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

    def _testing_datetime_it(self, typ):
        """The datetime type test success case
        """
        for protocol, attr in self._generate_protocol_attribute(typ):
            record = protocol.record
            name = '{}.{}'.format(record.__name__, attr)
            rec = record()

            value = typ.now()
            setattr(rec, attr, value)
            rc = getattr(rec, attr)
            self.assertEqual(value, rc,
                             'Mismatch: {} != {} ({})'.format(
                                 repr(value), repr(rc), name))
            
        
    def test_date_type(self):
        self._testing_datetime_it(DateType)

    def test_hourmin_type(self):
        self._testing_datetime_it(HourMinType)        

    def test_date_time_type(self):
        self._testing_datetime_it(DateTimeType)

    def test_status_type(self):
        self._testing_type_it(Status)

    def test_seat_type_classif_type(self):
        self._testing_type_it(SeatTypeClassif)        

    def test_putback_status_type(self):
        self._testing_type_it(PutbackStatus)

    def test_putback_type_type(self):
        self._testing_type_it(PutbackType)

    def test_achievement_status(self):
        self._testing_type_it(AchievementStatus)
