import logging
from collections import namedtuple
from datetime import date, time, datetime
from xml.sax.saxutils import unescape

from altair.skidata.decorators import SkidataXmlElement, SkidataXmlAttribute, SkidataXmlElementOrder
from altair.skidata.exceptions import SkidataUnmarshalFailed
from altair.skidata.unmarshaller import SkidataXmlUnmarshaller
from enum import Enum
from pyramid.decorator import reify

logger = logging.getLogger(__name__)


class SkidataDataType(Enum):
    """
    Skidata XML data types

    boolean: a Boolean value of either True or False
    dateTime: a date with time in a subset of the ISO 8601 format
    date: a date in a subset of the ISO 8601 format
    time: a time in a subset of the ISO 8601 format
    i4: a four-byte integer (-2147483648 to 2147483647)
    i8: an eight-byte integer (-9223372036854775808 to 9223372036854775807)
    string: a string
    """
    BOOLEAN = 0
    DATETIME = 1
    DATE = 2
    TIME = 3
    I4 = 4
    I8 = 5
    STRING = 6

    def format(self, value):
        """
        Format the given value by following the data type.
        :param value: value to be formatted
        :return
            value is NoneType
                -> empty
            BOOLEAN
                -> 0 or 1 (1=TRUE)
            DATETIME, DATE and TIME and value is an instance of either date or time
                -> ISO 8601 format
            I4, I8, STRING and others
                -> a unicode string
        """
        if isinstance(value, Enum):
            value = value.value

        if value is None:
            return ''
        elif self is SkidataDataType.BOOLEAN:
            return '1' if value else '0'
        elif self in (SkidataDataType.DATETIME, SkidataDataType.DATE) and isinstance(value, date):
            return value.isoformat()
        elif self is SkidataDataType.TIME and isinstance(value, time):
            return value.strftime('%H:%M')  # time has no second
        else:
            return unicode(value)

    def parse(self, value):
        """
        Parse the given value by following the data type.
        :param value: value to be parsed
        :return
            value is empty -> None
            BOOLEAN -> True or False ('1'=TRUE)
            DATETIME -> datetime
            DATE -> date
            TIME -> time
            I4, I8 -> integer
            STRING -> a unicode string
        """
        if not value:
            return None

        if self is SkidataDataType.BOOLEAN:
            return True if value == '1' else False
        elif self in (SkidataDataType.DATETIME, SkidataDataType.DATE, SkidataDataType.TIME):
            return self._parse_date_type(value)
        elif self in (SkidataDataType.I4, SkidataDataType.I8):
            return self._parse_int(value)
        else:
            return unicode(value)

    def _parse_date_type(self, value):
        if self is SkidataDataType.DATETIME:
            dt = self._parse_date_and_time(value, '%Y-%m-%dT%H:%M:%S') or \
                 self._parse_date_and_time(value, '%Y-%m-%dT%H:%M')
            return dt if isinstance(dt, datetime) else value

        elif self is SkidataDataType.DATE:
            dt = self._parse_date_and_time(value, '%Y-%m-%d')
            return dt.date() if isinstance(dt, datetime) else value

        elif self is SkidataDataType.TIME:
            dt = self._parse_date_and_time(value, '%H:%M')  # time has no second
            return dt.time() if isinstance(dt, datetime) else value

        return value

    @staticmethod
    def _parse_int(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return value

    @staticmethod
    def _parse_date_and_time(value, format_):
        try:
            return datetime.strptime(value, format_)
        except (ValueError, TypeError):
            return None


class TSPropertyType(Enum):
    """TSProperty types that exist in HSH"""

    # Standard types
    # EVENT: HSH does not make a difference between event types e.g. performances, games, matches, seasons etc,
    #        that means all of event types are categorized as EVENT.
    EVENT = 'EVENT'

    # Extended types configured by TS
    ORDER_NO = 'OrderNo'
    OPEN_DATE = 'OpenDate'
    START_DATE = 'StartDate'
    STOCK_TYPE = 'StockType'
    PRODUCT_NAME = 'ProductName'
    PRODUCT_ITEM_NAME = 'ProductItemName'
    GATE = 'Gate'
    SEAT_NAME = 'SeatName'
    SALES_SEGMENT = 'SalesSegment'
    TICKET_TYPE = 'TicketType'
    PERSON_CATEGORY = 'PersonCategory'


# TSOption is an extended TSProperty configured by TS
# TSOption is represented as TSProperty Element as following
# E.g.:
# <TSProperty Type="OrderNo">
#   <ID>RE0000000001</ID>
# </TSProperty>
#
# namedtuple to store TSOption values
# Field names are what TSProperty names are downcased
TSOption = namedtuple('TSOption', [n.lower() for n in TSPropertyType.__members__.keys()])
TSOption.__new__.__defaults__ = (None,) * len(TSPropertyType)  # Allow to instantiate with partial values


class TSAction(Enum):
    """
    Action information which represents information how to process the sent data
    Action Element defines these data in XML
        E.g.: <Action>I</Action>

    Insert - Inserts the information into HSH
    Delete - Deletes the information from HSH
    Update - HSH updates existing information.
    """
    INSERT = 'I'
    DELETE = 'D'
    UPDATE = 'U'


class TSCoding(Enum):
    """
    Coding which is enumeration for type of ticket, Code to identify a real ticket
    Coding Element defines these data in XML
        E.g.: <Coding>270</Coding>
    """
    VISIBLE_EAN = 260
    VISIBLE_QR_CODE = 270


class BlockingType(Enum):
    """
    Blocking types for ticket.

    Data Carrier blocking blocks all associated permissions.
    Permission blocking blocks only a certain permission of the ticket.
    """
    DATA_CARRIER = 0
    PERMISSION = 1


class BlockingReason(Enum):
    BLOCKED = 0       # ticket blocked
    STOLEN = 1        # ticket was stolen
    LOST = 2          # ticket was lost
    CANCELED = 3      # ticket was cancelled
    RENEWED = 4       # ticket was renewed
    NOT_PAID = 5      # ticket was not paid
    NOT_EXTENDED = 6  # ticket not extended
    EXCHANGED = 7     # ticket was exchanged
    SUBSTITUTE = 8    # substitute ticket
    TERMINATED = 9    # terminated


class HSHErrorType(Enum):
    """HSH Error types"""
    STOP = 'S'     # Critical Error (Stop), import is aborted
    ERROR = 'E'    # Error
    WARNING = 'W'  # Warning


class HSHErrorNumber(Enum):
    """
    HSH Error numbers

    10000 to 19999 represent Critical Error
    20000 to 29999 represent Error
    30000 to 39999 represent Warning
    """
    UNKNOWN_RECORD_TYPE = 10000
    UNKNOWN_INTERFACE_VERSION = 10001
    UNKNOWN_TICKETING_SERVER = 10002
    DUPLICATE_ID = 10003
    INVALID_XML_RECORD = 10004
    HSH_INTERNAL_ERROR = 11000
    HSH_DATABASE_ERROR = 11001
    INVALID_ACTION_TYPE = 20000
    UNKNOWN_XML_ELEMENT = 20001
    INVALID_DATA_TYPE = 20003
    MISSING_MANDATORY_FIELD = 20004
    MISSING_KEY_COLUMN = 20005
    UNKNOWN_EVENT_ID = 20006
    UNKNOWN_AREA_ID = 20007
    UNKNOWN_PERSON_ID = 20008
    INVALID_CODING = 20009
    INVALID_BLOCKING_TYPE = 20010
    INVALID_BLOCKING_REASON = 20011
    TS_PROPERTY_ALREADY_IN_USE = 20012
    WHITELIST_UPDATE_NOT_POSSIBLE = 20013
    NON_EXISTING_PERMISSION = 20014
    NON_EXISTING_PHOTO_ID = 20015
    INVALID_ATTRIBUTE_VALUE = 20016
    NON_EXISTING_TS_PROPERTY = 30000
    ALREADY_EXISTING_TS_PROPERTY = 30001
    TS_PROPERTY_TYPE_ALREADY_EXISTS = 30002
    RECORD_DOES_NOT_EXIST = 30003


class Arguments(object):
    """
    Arguments can be used to provide additional information for events.
    The arguments element contains place, date and time information for an event.
    """
    def __init__(self, place=None, from_date=None, from_time=None, to_date=None, to_time=None):
        """
        :param place: Place of event
        :param from_date: date object, Begin date of event
        :param from_time: time object, Begin time of event
        :param to_date: date object, End date of event
        :param to_time: time object, End time of event
        """
        self._place = place
        self._from_date = from_date
        self._from_time = from_time
        self._to_date = to_date
        self._to_time = to_time

    @SkidataXmlElement(required=False, maxlength=100)
    def place(self):
        return self._place

    def set_place(self, value):
        self._place = value

    @SkidataXmlElement(required=False, data_type=SkidataDataType.DATE)
    def from_date(self):
        return self._from_date

    def set_from_date(self, value):
        self._from_date = value

    @SkidataXmlElement(required=False, data_type=SkidataDataType.TIME)
    def from_time(self):
        return self._from_time

    def set_from_time(self, value):
        self._from_time = value

    @SkidataXmlElement(required=False, data_type=SkidataDataType.DATE)
    def to_date(self):
        return self._to_date

    def set_to_date(self, value):
        self._to_date = value

    @SkidataXmlElement(required=False, data_type=SkidataDataType.TIME)
    def to_time(self):
        return self._to_time

    def set_to_time(self, value):
        self._to_time = value


class TSProperty(object):
    """
    The TSProperty element is imported and mapped to HSProperty within the HSH configuration.
    """
    def __init__(self, type_=None, property_id=None, expire=None):
        """
        :param type_: TSPropertyType
        :param property_id: a unique value by Type
        :param expire: datetime object, Date when the data is archived
        """
        self._type = type_
        self._property_id = property_id
        self._expire = expire

    @SkidataXmlAttribute(maxlength=100)
    def type(self):
        return self._type

    def set_type(self, value):
        self._type = value

    @SkidataXmlElement(name='ID', maxlength=100)
    def property_id(self):
        return self._property_id

    def set_property_id(self, value):
        self._property_id = value

    @SkidataXmlAttribute(required=False, data_type=SkidataDataType.DATETIME)
    def expire(self):
        return self._expire

    def set_expire(self, value):
        self._expire = value

    def unmarshal_type(self, value):
        self._type = TSPropertyType(value) if value in [t.value for t in TSPropertyType] else value


@SkidataXmlElement(name=TSProperty.__name__)
class EventTSProperty(TSProperty):
    """The extended TSProperty element is for Event setup."""
    def __init__(self, action=None, property_id=None, name=None, expire=None, arguments=None):
        """
        :param action: TSAction
        :param property_id: a unique value by Type
        :param name: an Event name
        :param expire: datetime object, Date when the data is archived
        :param arguments: Arguments object
        """
        self._action = action
        self._name = name
        self._arguments = arguments

        super(EventTSProperty, self).__init__(type_=TSPropertyType.EVENT,
                                              property_id=property_id,
                                              expire=expire)

    @SkidataXmlElement
    def action(self):
        return self._action

    def set_action(self, value):
        self._action = value

    @SkidataXmlElement(maxlength=100)
    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    @SkidataXmlElement(required=False, cls=Arguments)
    def arguments(self):
        return self._arguments

    def set_arguments(self, value):
        self._arguments = value

    def unmarshal_action(self, value):
        self._action = TSAction(value) if value in [a.value for a in TSAction] else value


class Permission(object):
    """The permission describes the ticket"""
    def __init__(self, upid=None, ts_property=None):
        """
        :param upid: Unique Permission ID, recommended to start with 1 and increment by 1
        :param ts_property: TSProperty object or a list of TSProperty objects
        """
        self._upid = upid
        self._ts_property = ts_property

    @SkidataXmlElement(name='UPID', maxlength=100)
    def upid(self):
        return self._upid

    def set_upid(self, value):
        self._upid = value

    @SkidataXmlElement(required=False, multi=True, cls=TSProperty)
    def ts_property(self):
        return self._ts_property

    def set_ts_property(self, value):
        self._ts_property = value


class WhitelistRecord(object):
    """The WhitelistRecord element is for the ticket to be allowed for entry"""
    def __init__(self, action=None, utid=None, coding=TSCoding.VISIBLE_QR_CODE, permission=None, expire=None):
        """
        :param action: TSAction
        :param utid: Unique ticket-ID (QR code)
        :param coding: TSCoding
        :param permission: Permission object or a list of Permission objects
        :param expire: datetime object, Date when the data is archived
        """
        self._action = action
        self._utid = utid
        self._coding = coding
        self._permission = permission
        self._expire = expire

    @SkidataXmlElement
    def action(self):
        return self._action

    def set_action(self, value):
        self._action = value

    @SkidataXmlElement(name='UTID', maxlength=100)
    def utid(self):
        return self._utid

    def set_utid(self, value):
        self._utid = value

    @SkidataXmlElement(data_type=SkidataDataType.I4)
    def coding(self):
        return self._coding

    def set_coding(self, value):
        self._coding = value

    @SkidataXmlElement(required=False, multi=True, cls=Permission)
    def permission(self):
        return self._permission

    def set_permission(self, value):
        self._permission = value

    @SkidataXmlAttribute(required=False, data_type=SkidataDataType.DATETIME)
    def expire(self):
        return self._expire

    def set_expire(self, value):
        self._expire = value

    def unmarshal_action(self, value):
        self._action = TSAction(value) if value in [a.value for a in TSAction] else value

    def unmarshal_coding(self, value):
        self._coding = TSCoding(value) if value in [c.value for c in TSCoding] else value


@SkidataXmlElement(name=WhitelistRecord.__name__)
class BlockingWhitelistRecord(WhitelistRecord):
    """
    This extended WhitelistRecord element is for identifying the blocked ticket or permission.
    Action is unnecessary for blacklist.
    """
    @SkidataXmlElement(required=False)
    def action(self):
        return self._action


class BlacklistRecord(object):
    """The tickets listed in the Blacklist are not allowed to enter"""
    def __init__(self, action=None, blocking_whitelist=None, blocking_type=BlockingType.PERMISSION, reason=None,
                 from_=None, to=None, display_message=None, comment=None, operator_message=None, expire=None):
        """
        :param action: TSAction
        :param blocking_whitelist: BlockingWhitelistRecord object
        :param blocking_type: BlockingType
        :param reason: BlockingReason
        :param from_: datetime object, Beginning of blocking
        :param to: datetime object, End of blocking.
                   Mandatory when blocking_type is BlockingType.DATA_CARRIER
        :param display_message: 2 Lines with max.14 characters per line
                                can be shown on the display of the reader ASx70.
                                '\n' is used to separate the lines
        :param comment: Additional information shown to operator
        :param operator_message: Additional information shown to operator
        :param expire: datetime object, Date when the data is archived
        """
        self._action = action
        self._blocking_whitelist = blocking_whitelist
        self._blocking_type = blocking_type
        self._reason = reason
        self._from = from_
        self._to = to
        self._display_message = display_message
        self._comment = comment
        self._operator_message = operator_message
        self._expire = expire

    @SkidataXmlElement
    def action(self):
        return self._action

    def set_action(self, value):
        self._action = value

    @SkidataXmlElement(name=WhitelistRecord.__name__, cls=BlockingWhitelistRecord)
    def blocking_whitelist(self):
        return self._blocking_whitelist

    def set_blocking_whitelist(self, value):
        self._blocking_whitelist = value

    @SkidataXmlElement(data_type=SkidataDataType.I4)
    def blocking_type(self):
        return self._blocking_type

    def set_blocking_type(self, value):
        self._blocking_type = value

    @SkidataXmlElement(data_type=SkidataDataType.I4)
    def blocking_reason(self):
        return self._reason

    def set_blocking_reason(self, value):
        self._reason = value

    @SkidataXmlElement(required=False, data_type=SkidataDataType.DATETIME)
    def get_from(self):
        return self._from

    def set_from(self, value):
        self._from = value

    @SkidataXmlElement(required=False, data_type=SkidataDataType.DATETIME)
    def get_to(self):
        return self._to

    def set_to(self, value):
        self._to = value

    @SkidataXmlElement(required=False, maxlength=100)
    def display_message(self):
        return self._display_message

    def set_display_message(self, value):
        self._display_message = value

    @SkidataXmlElement(required=False, maxlength=100)
    def comment(self):
        return self._comment

    def set_comment(self, value):
        self._comment = value

    @SkidataXmlElement(required=False, maxlength=100)
    def operator_message(self):
        return self._operator_message

    def set_operator_message(self, value):
        self._operator_message = value

    @SkidataXmlAttribute(required=False, data_type=SkidataDataType.DATETIME)
    def expire(self):
        return self._expire

    def set_expire(self, value):
        self._expire = value

    def unmarshal_action(self, value):
        self._action = TSAction(value) if value in [a.value for a in TSAction] else value

    def unmarshal_blocking_type(self, value):
        if value in [str(t.value) for t in BlockingType]:
            self._blocking_type = BlockingType(int(value))
        else:
            self._blocking_type = value

    def unmarshal_blocking_reason(self, value):
        if value in [str(r.value) for r in BlockingReason]:
            self._reason = BlockingReason(int(value))
        else:
            self._reason = value


class Header(object):
    """
    The Header element contains the partner (TS) information (sender and receiver),
    the HSH interface version and the ID number.
    """
    def __init__(self, version=None, issuer=None, receiver=None, request_id=None):
        """
        :param version: Interface Version, fix keyword defined by HSH
        :param issuer: Sender of a telegram, set in the HSH configuration
        :param receiver: Receiver of a telegram, set in the HSH configuration
        :param request_id: Unique ID for XML-Data generated by TS
        """
        self._version = version
        self._issuer = issuer
        self._receiver = receiver
        self._request_id = request_id

    @SkidataXmlElement(maxlength=100)
    def version(self):
        return self._version

    def set_version(self, value):
        self._version = value

    @SkidataXmlElement(maxlength=100)
    def issuer(self):
        return self._issuer

    def set_issuer(self, value):
        self._issuer = value

    @SkidataXmlElement(maxlength=100)
    def receiver(self):
        return self._receiver

    def set_receiver(self, value):
        self._receiver = value

    @SkidataXmlElement(name='ID', required=False, data_type=SkidataDataType.I4)
    def request_id(self):
        return self._request_id

    def set_request_id(self, value):
        self._request_id = value


@SkidataXmlElementOrder(func_names=['number', 'description', 'event_ts_property', 'whitelist', 'blacklist'])
class Error(object):
    """The Error element contains information about incorrect and irregular situations during the import process"""
    def __init__(self, type_=None, number=None, description=None,
                 event_ts_property=None, whitelist=None, blacklist=None):
        """
        TSProperty and WhitelistRecord which failed to import to HSH are contained
        :param type_: HSHErrorType
        :param number: HSHErrorNumber
        :param description: an error description
        :param event_ts_property: EventTSProperty object
        :param whitelist: WhitelistRecord object or a list of WhitelistRecord objects
        :param blacklist: BlacklistRecord object or a list of BlacklistRecord objects
        """
        self._type = type_
        self._number = number
        self._description = description
        self._event_ts_property = event_ts_property
        self._whitelist = whitelist
        self._blacklist = blacklist

    @SkidataXmlAttribute
    def type(self):
        return self._type

    def set_type(self, value):
        self._type = value

    @SkidataXmlElement(data_type=SkidataDataType.I4)
    def number(self):
        return self._number

    def set_number(self, value):
        self._number = value

    @SkidataXmlElement(required=False)
    def description(self):
        return self._description

    def set_description(self, value):
        self._description = value

    @SkidataXmlElement(name=TSProperty.__name__, required=False, cls=EventTSProperty)
    def event_ts_property(self):
        return self._event_ts_property

    def set_event_ts_property(self, value):
        self._event_ts_property = value

    @SkidataXmlElement(required=False, multi=True, cls=WhitelistRecord)
    def whitelist(self):
        return self._whitelist

    @SkidataXmlElement(required=False, multi=True, cls=BlacklistRecord)
    def blacklist(self):
        return self._blacklist

    def set_blacklist(self, value):
        self._blacklist = value

    def set_whitelist(self, value):
        self._whitelist = value

    def unmarshal_type(self, value):
        if value in [t.value for t in HSHErrorType]:
            self._type = HSHErrorType(value)
        else:
            self._type = value

    def unmarshal_number(self, value):
        if value in [str(n.value) for n in HSHErrorNumber]:
            self._number = HSHErrorNumber(int(value))
        else:
            self._number = value


@SkidataXmlElementOrder(func_names=['header', 'event_ts_property', 'whitelist', 'blacklist'])
class TSData(object):
    """TSData is the basic element for all telegrams sent from the TS"""
    def __init__(self, header=None, event_ts_property=None, whitelist=None, blacklist=None):
        """
        :param header: Header object
        :param event_ts_property: EventTSProperty object
        :param whitelist: WhitelistRecord object or a list of WhitelistRecord objects
        :param blacklist: BlacklistRecord object or a list of BlacklistRecord objects
        """
        self._header = header
        self._event_ts_property = event_ts_property
        self._whitelist = whitelist
        self._blacklist = blacklist

    @SkidataXmlElement(cls=Header)
    def header(self):
        return self._header

    def set_header(self, value):
        self._header = value

    @SkidataXmlElement(name=TSProperty.__name__, required=False, multi=True, cls=EventTSProperty)
    def event_ts_property(self):
        return self._event_ts_property

    def set_event_ts_property(self, value):
        self._event_ts_property = value

    @SkidataXmlElement(required=False, multi=True, cls=WhitelistRecord)
    def whitelist(self):
        return self._whitelist

    def set_whitelist(self, value):
        self._whitelist = value

    @SkidataXmlElement(required=False, multi=True, cls=BlacklistRecord)
    def blacklist(self):
        return self._blacklist

    def set_blacklist(self, value):
        self._blacklist = value


@SkidataXmlElementOrder(func_names=['header', 'error'])
class HSHData(object):
    """HSHData is the basic element for all response telegrams sent by HSH"""
    def __init__(self, header=None, error=None):
        """
        :param header: Header object
        :param error: Error object
        """
        self._header = header
        self._error = error

    @SkidataXmlElement(cls=Header)
    def header(self):
        return self._header

    def set_header(self, value):
        self._header = value

    @SkidataXmlElement(required=False, multi=True, cls=Error)
    def error(self):
        return self._error

    def set_error(self, value):
        self._error = value


class ProcessRequest(object):
    """ProcessRequest is SOAP Action defined in Skidata WebService WSDL."""
    def __init__(self, ts_data=None):
        self._ts_data = ts_data

    @SkidataXmlElement(name='request')
    def ts_data(self):
        return self._ts_data

    def set_ts_data(self, value):
        self._ts_data = value

    def unmarshal_ts_data(self, value):
        ts_data = SkidataXmlUnmarshaller.unmarshal(unescape(value), TSData)
        self._ts_data = ts_data


class ProcessRequestResponse(object):
    """ProcessResponse is SOAP Action defined in Skidata WebService WSDL."""
    def __init__(self, hsh_data=None):
        self._hsh_data = hsh_data

    @SkidataXmlElement(name='ProcessRequestResult')
    def hsh_data(self):
        return self._hsh_data

    def set_hsh_data(self, value):
        self._hsh_data = value

    def unmarshal_hsh_data(self, value):
        hsh_data = SkidataXmlUnmarshaller.unmarshal(unescape(value), HSHData)
        self._hsh_data = hsh_data


class Body(object):
    def __init__(self, process_request=None, process_response=None):
        self._process_request = process_request
        self._process_response = process_response

    @SkidataXmlElement(namespace='http://tempuri.org/', cls=ProcessRequest, required=False)
    def process_request(self):
        return self._process_request

    def set_process_request(self, value):
        self._process_request = value

    @SkidataXmlElement(namespace='http://tempuri.org/', cls=ProcessRequestResponse, required=False)
    def process_response(self):
        return self._process_response

    def set_process_response(self, value):
        self._process_response = value


@SkidataXmlElement(namespace='http://schemas.xmlsoap.org/soap/envelope/')
class Envelope(object):
    """Envelope is the root element."""
    def __init__(self, body=None):
        self._body = body

    @SkidataXmlElement(namespace='http://schemas.xmlsoap.org/soap/envelope/', cls=Body)
    def body(self):
        return self._body

    def set_body(self, value):
        self._body = value


class SkidataWebServiceResponse(object):
    """Skidata Web Service Response"""
    def __init__(self, status_code, text):
        self._status_code = status_code
        self._text = text

    @property
    def status_code(self):
        return self._status_code

    @property
    def text(self):
        """Content of the response"""
        return self._text

    @property
    def success(self):
        hsh_data = self.hsh_data
        return self.status_code == 200 and isinstance(hsh_data, HSHData)\
            and isinstance(hsh_data.header(), Header) and hsh_data.error() is None

    @reify
    def envelope(self):
        try:
            return SkidataXmlUnmarshaller.unmarshal(self.text, Envelope)
        except SkidataUnmarshalFailed:
            return None

    @property
    def hsh_data(self):
        envelope = self.envelope
        if not isinstance(envelope, Envelope):
            return None

        body = envelope.body()
        if not isinstance(body, Body):
            return None

        process_response = body.process_response()
        if not isinstance(process_response, ProcessRequestResponse):
            return None

        return process_response.hsh_data()

    def errors(self):
        """Return all errors by a list"""
        hsh_data = self.hsh_data
        if not isinstance(hsh_data, HSHData) or self.success:
            return []

        error = hsh_data.error()
        return error if isinstance(error, list) else [error]
