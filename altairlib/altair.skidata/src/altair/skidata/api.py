from datetime import datetime, time, date

from altair.skidata.models import TSOption, TSProperty, Permission, WhitelistRecord, TSCoding, \
    TSPropertyType, Arguments, EventTSProperty, BlacklistRecord, BlockingWhitelistRecord, BlockingType


def make_ts_property(ts_option):
    """
    Make a TSProperty object which is used to represent TSOption
    :param ts_option: TSOption
    """
    if not isinstance(ts_option, TSOption):
        return None

    ts_properties = []
    for property_type in TSPropertyType.__members__.values():
        option_value = getattr(ts_option, property_type.name.lower(), None)
        # Format start and open date
        if property_type in (TSPropertyType.OPEN_DATE, TSPropertyType.START_DATE) and \
                isinstance(option_value, datetime):
            option_value = option_value.strftime('%Y/%m/%d %H:%M')

        if option_value is not None:
            ts_property = TSProperty(type_=property_type, property_id=option_value)
            ts_properties.append(ts_property)

    if len(ts_properties) == 1:
        ts_properties = ts_properties[0]

    return ts_properties or None


def make_event_ts_property(action, event_id, name, expire=None,
                           place=None, start_date_or_time=None, end_date_or_time=None):
    """
    Make an EventTSProperty object to represent Event information.
    :param action: TSAction
    :param event_id: a unique ID of event (ORG short code + start date of event)
        -> E.g.: RE202005011400 in case that start date of Eagles game is 2019-05-01 14:00
    :param name: Name of event
    :param expire: datetime object, Date when the data is archived (invalidated)
    :param place: Place of event
    :param start_date_or_time: date, datetime or time object, Begin date and time of event
        -> time information is set when datetime or time object is given
    :param end_date_or_time: date, datetime or time object, End date and time of event
        -> time information is set when datetime or time object is given
    """
    arguments = Arguments(place=place)
    if isinstance(start_date_or_time, datetime):
        arguments.set_from_date(start_date_or_time.date())
    elif isinstance(start_date_or_time, date):
        arguments.set_from_date(start_date_or_time)

    if isinstance(start_date_or_time, (datetime, time)):
        arguments.set_from_time(start_date_or_time.time())

    if isinstance(end_date_or_time, datetime):
        arguments.set_to_date(end_date_or_time.date())
    elif isinstance(end_date_or_time, date):
        arguments.set_to_date(end_date_or_time)

    if isinstance(end_date_or_time, (datetime, time)):
        arguments.set_to_time(end_date_or_time.time())

    return EventTSProperty(action=action, property_id=event_id,
                           name=name, expire=expire, arguments=arguments)


def make_permission(upid, ts_option=None):
    """
    Make a Permission object
    :param upid: Unique Permission ID, recommended to start with 1 and increment by 1
    :param ts_option: TSOption
    """
    return Permission(upid=upid, ts_property=make_ts_property(ts_option))


def make_whitelist(action, qr_code, coding=TSCoding.VISIBLE_QR_CODE, ts_option=None, expire=None):
    """
    Make a WhitelistRecord object
    :param action: TSAction
    :param qr_code: QR code data
    :param coding: TSCoding
    :param ts_option: TSOption object
    :param expire: datetime object, Date when the data is archived (invalidated)
    """
    if isinstance(ts_option, TSOption):
        permission = make_permission(upid=1, ts_option=ts_option)
    else:
        permission = None

    return WhitelistRecord(action=action, utid=qr_code, coding=coding,
                           permission=permission, expire=expire)


def make_blacklist(action, qr_code, blocking_reason, blocking_type=BlockingType.PERMISSION,
                   coding=TSCoding.VISIBLE_QR_CODE, from_=None, to=None,
                   display_message=None, comment=None, operator_message=None, expire=None):
    """
    Make a BlacklistRecord object
    :param action: TSAction
    :param qr_code: QR code data
    :param blocking_reason: BlockingReason
    :param blocking_type: BlockingType
    :param coding: TSCoding
    :param from_: datetime object, Beginning of blocking
    :param to: datetime object, End of blocking.
               Required when blocking_type is BlockingType.DATA_CARRIER
    :param display_message: string
    :param comment: string
    :param operator_message: string
    :param expire: datetime object, Date when the data is archived
    """
    # Currently support single Permission and set UPID to 1
    blocking_whitelist = BlockingWhitelistRecord(utid=qr_code, coding=coding,
                                                 permission=make_permission(upid=1))

    return BlacklistRecord(action=action, blocking_whitelist=blocking_whitelist, blocking_type=blocking_type,
                           reason=blocking_reason, from_=from_, to=to, display_message=display_message,
                           comment=comment, operator_message=operator_message, expire=expire)
