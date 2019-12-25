#! /usr/bin/env python
# coding=utf-8
import logging
from argparse import ArgumentParser
from datetime import datetime

from altair.app.ticketing.core.models import Performance, Organization, Event, EventSetting, OrganizationSetting
from altair.skidata.api import make_event_ts_property
from altair.skidata.exceptions import SkidataWebServiceError
from altair.skidata.models import TSAction, HSHErrorType, HSHErrorNumber
from altair.skidata.sessions import skidata_webservice_session
from altair.sqlahelper import get_db_session
from pyramid.paster import setup_logging, bootstrap
from sqlalchemy import extract

logger = logging.getLogger(__name__)


def _concat_perf(performance_id_list):
    performance_id_list.sort()
    return ', '.join([str(p_id) for p_id in performance_id_list])


def _conv_date_str(value, parser):
    if value is not None:
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            parser.error("date '{}' does not match format '%Y-%m-%d'".format(value))


def skidata_event_query(session, performance_id_list=None, year=None, from_date=None, to_date=None):
    """SKIDATA へ追加する公演を検索するクエリを構築する
    SKIDATA 連携条件
    - SKIDATA連携ON
    - パフォーマンスIDの指定がある場合は Performance.id で対象を絞る
    - 開演年の指定がある場合は Performance.start_on の year で対象を絞る
    - 開演日の指定がある場合は Performance.start_on が from_date から to_date までの範囲に絞る
    """
    criterion = [
        EventSetting.enable_skidata == 1,
        OrganizationSetting.enable_skidata == 1
    ]
    if performance_id_list:
        criterion.append(Performance.id.in_(performance_id_list))
    if year is not None:
        criterion.append(extract('year', Performance.start_on) == year)
    if from_date is not None:
        criterion.append(Performance.start_on >= from_date)
    if to_date is not None:
        criterion.append(Performance.start_on <= to_date)

    return session\
        .query(Performance.id.label('performance_id'),
               Performance.name,
               Performance.start_on,
               Organization.code)\
        .join(Event, Event.id == Performance.event_id)\
        .join(EventSetting, EventSetting.event_id == Event.id)\
        .join(Organization, Organization.id == Event.organization_id)\
        .join(OrganizationSetting, OrganizationSetting.organization_id == Organization.id)\
        .filter(*criterion)


def send_skidata_event_request(skidata_session, event_ts_properties, event_map):
    try:
        resp = skidata_session.send(event_ts_property=event_ts_properties)
        log_skidata_event_resp(resp, event_map)
    except SkidataWebServiceError as e:
        performance_id_list = []
        for p_id_list in event_map.values():
            performance_id_list.extend(p_id_list)

        logger.error('%s (Performance ID: %s)', e, _concat_perf(performance_id_list))


def log_skidata_event_resp(skidata_resp, event_map):
    logger.debug(u'Skidata EVENT Import result: %s', skidata_resp.text)

    if skidata_resp is None or skidata_resp.success:
        performance_id_list = []
        for p_id_list in event_map.values():
            performance_id_list.extend(p_id_list)

        logger.debug('Performance inserted as Skidata EVENT successfully '
                     '(Performance ID: %s)', _concat_perf(performance_id_list))
    else:
        log_hsh_error(skidata_resp.errors, event_map)


def log_hsh_error(hsh_error_list, event_map):
    messages = []
    failed_id_list = []
    for error in hsh_error_list:
        error_type = error.type().value \
            if isinstance(error.type(), HSHErrorType) else error.type()
        error_number = error.number().value \
            if isinstance(error.number(), HSHErrorNumber) else error.number()

        msg = u'Error Type: {type}, Number: {number}, Description: {description}.' \
            .format(type=error_type, number=error_number, description=error.description())

        ts_property = error.event_ts_property()
        if ts_property is not None:
            performance_id_list = event_map.get(ts_property.property_id(), [])
            failed_id_list.extend(performance_id_list)
            messages.append(u'{} (Performance ID: {})'.format(msg, _concat_perf(performance_id_list)))
        else:
            messages.append('An unexpected error has occurred: {}'.format(msg))

    if messages:
        logger.error('Performance failed to be inserted as Skidata EVENT '
                     '(Performance ID: %s) Details: %s', _concat_perf(failed_id_list), '\n'.join(messages))


def insert_skidata_event(request, performance_id_list, year, from_date, to_date):
    """Skidata HSH へ EVENT を追加する"""
    session = get_db_session(request, name='slave')
    skidata_session = skidata_webservice_session(request.registry.settings)
    events = []
    event_map = {}
    for data in skidata_event_query(session, performance_id_list, year, from_date, to_date):
        # Expire は公演の開演年の最終日時
        expire = datetime(year=data.start_on.year, month=12, day=31, hour=23, minute=59, second=59)
        start_date = data.start_on.strftime('%Y%m%d%H%M')
        event_code = '{code}{start_date}'.format(code=data.code, start_date=start_date)

        suffix = ' ' + data.start_on.strftime('%Y/%m/%d')
        # EVENT名は「公演名＋空白＋開演日」
        # EVENT名は100文字までしか登録されないので、日付が正しく登録されるように余分な部分はカットします
        event_name = data.name[:100-len(suffix)] + suffix

        events.append(make_event_ts_property(
            action=TSAction.INSERT, event_id=event_code, name=event_name,
            expire=expire, start_date_or_time=data.start_on.date()
        ))

        if event_code in event_map:
            event_map[event_code].append(data.performance_id)
        else:
            event_map[event_code] = [data.performance_id]

        # 最大 1000 件単位で EVENT 送信します
        if len(events) >= 1000:
            send_skidata_event_request(skidata_session, events, event_map)

            events = []
            event_map.clear()

    if events:
        send_skidata_event_request(skidata_session, events, event_map)


def main():
    """SKIDATA EVENT 追加スクリプト
    以下のオプションで指定した範囲内で開演する公演の情報を SKIDATA へ送信する

    -c/--config : 設定ファイルのパス（必須）。
    -y/--year : 指定の年に開演する公演を SKIDATA へ追加
    -p/--performance : SKIDATA へ追加する公演ID。スペースで複数指定が可能
    -f/--from : 指定の日以降に開演する公演を SKIDATA へ追加（%Y-%m-%d）
    -t/--to : 指定の日までに開演する公演を SKIDATA へ追加（%Y-%m-%d）

    --year と --performance の指定が無い場合は、--from と --to が必須
    """
    parser = ArgumentParser(description='Insert Skidata EVENT to HSH.')
    parser.add_argument('-c', '--config', type=str, required=True,
                        help='config file')
    parser.add_argument('-y', '--year', type=int, required=False,
                        help='year of start_on of performance supposed to be inserted into SKIDATA')
    parser.add_argument('-p', '--performance', type=int, nargs='+', required=False,
                        help='performance ID(s) to be inserted into SKIDATA')
    parser.add_argument('-f', '--from', dest='from_date', required=False,
                        type=lambda v: _conv_date_str(v, parser),
                        help="target date '%%Y-%%m-%%d' after which performances start")
    parser.add_argument('-t', '--to', dest='to_date', required=False,
                        type=lambda v: _conv_date_str(v, parser),
                        help="target date '%%Y-%%m-%%d' by which performances start")

    args = parser.parse_args()
    # year と performance オプションがない場合は from & to オプションが必須
    if not args.performance and args.year is None and (args.from_date is None or args.to_date is None):
        parser.error('-f/--from and -t/--to required')

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    insert_skidata_event(request, args.performance, args.year, args.from_date, args.to_date)
