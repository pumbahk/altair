# -*- coding:utf-8 -*-

import argparse
import sys
import os
import logging
from datetime import date, datetime
from sqlalchemy.orm.exc import NoResultFound
from pyramid.paster import bootstrap, setup_logging
from pyramid.renderers import render
from altair.mailhelpers import Mailer
from altair.sqlahelper import get_global_db_session
from ..mdm.shop_master import make_unmarshaller
from ..datainterchange.fileio import MarshalErrorBase
from ..datainterchange.importing import ImportSession, normal_file_filter

logger = logging.getLogger(__name__)

localized_field_names = {
    'shop_code': u'店番',
    'shop_code_updated': u'店番変更フラグ',
    'company_code': u'会社コード',
    'company_code_updated': u'会社コード変更フラグ',
    'company_name': u'会社名',
    'company_name_updated': u'会社名変更フラグ',
    'district_code': u'ディストリクトコード',
    'district_code_updated': u'ディストリクトコード変更フラグ',
    'district_name': u'ディストリクト名',
    'district_name_updated': u'ディストリクト名変更フラグ',
    'district_valid_from': u'ディストリクト有効開始日',
    'district_valid_from_updated': u'ディストリクト有効開始日変更フラグ',
    'branch_code': u'営業所コード',
    'branch_code_updated': u'営業所コード変更フラグ',
    'branch_name': u'営業所名称',
    'branch_name_updated': u'営業所名称変更フラグ',
    'branch_valid_from': u'営業所有効開始日',
    'branch_valid_from_updated': u'営業所有効開始日変更フラグ',
    'shop_name': u'店名',
    'shop_name_updated': u'店名変更フラグ',
    'shop_name_kana': u'店名フリガナ',
    'shop_name_kana_updated': u'店名フリガナ変更フラグ',
    'shop_tel': u'電話番号',
    'shop_tel_updated': u'電話番号変更フラグ',
    'prefecture_code': u'都道府県コード',
    'prefecture_code_updated': u'都道府県コード変更フラグ',
    'prefecture_name': u'都道府県名称',
    'prefecture_name_updated': u'都道府県名称変更フラグ',
    'shop_address': u'店舗住所',
    'shop_address_updated': u'店舗住所変更フラグ',
    'shop_open_from': u'絶対店舗開店日',
    'shop_open_from_updated': u'絶対店舗開店日変更フラグ',
    'zip': u'郵便番号 (ハイフンあり)',
    'zip_updated': u'郵便番号変更フラグ',
    'business_run_from': u'店舗運営開始日',
    'business_run_from_updated': u'店舗運営開始日変更フラグ',
    'shop_open_at': u'開店時刻',
    'shop_open_at_updated': u'開店時刻変更フラグ',
    'shop_close_at': u'閉店時刻',
    'shop_close_at_updated': u'閉店時刻変更フラグ',
    'business_hours': u'営業時間',
    'business_hours_updated': u'営業時間変更フラグ',
    'opens_24hours': u'24時間営業フラグ',
    'opens_24hours_updated': u'24時間営業フラグ変更フラグ',
    'closest_station': u'最寄駅',
    'closest_station_updated': u'最寄駅変更フラグ',
    'liquor_available': u'酒免許有無',
    'liquor_available_updated': u'酒免許有無変更フラグ',
    'cigarettes_available': u'煙草免許有無',
    'cigarettes_available_updated': u'煙草免許有無変更フラグ',
    'business_run_until': u'店舗運営終了日',
    'business_run_until_updated': u'店舗運営終了日変更フラグ',
    'shop_open_until': u'絶対店舗閉鎖日',
    'shop_open_until_updated': u'絶対店舗閉鎖日変更フラグ',
    'business_paused_at': u'一時閉鎖日',
    'business_paused_at_updated': u'一時閉鎖日変更フラグ',
    'business_continued_at': u'店舗再開店日',
    'business_continued_at_updated': u'店舗再開店日変更フラグ',
    'latitude': u'緯度',
    'latitude_updated': u'緯度変更フラグ',
    'longitude': u'経度',
    'longitude_updated': u'経度変更フラグ',
    'atm_available': u'ATM有無',
    'atm_available_updated': u'ATM有無変更フラグ',
    'mmk_available': u'MMK有無',
    'mmk_available_updated': u'MMK有無変更フラグ',
    'atm_available_from': u'ATMサービス開始日',
    'atm_available_from_updated': u'ATMサービス開始日変更フラグ',
    'mmk_available_from': u'MMKサービス開始日',
    'mmk_available_from_updated': u'MMKサービス開始日変更フラグ',
    'atm_available_until': u'ATMサービス終了日',
    'atm_available_until_updated': u'ATMサービス終了日変更フラグ',
    'mmk_available_until': u'MMKサービス終了日',
    'mmk_available_until_updated': u'MMKサービス終了日変更フラグ',
    'renewal_start_at': u'改装開始日',
    'renewal_start_at_updated': u'改装開始日変更フラグ',
    'renewal_end_at': u'改装終了日',
    'renewal_end_at_updated': u'改装終了日変更フラグ',
    'record_updated': u'レコード変更有無',
    'status': u'店舗運営ステータス',
    'paused': u'一時閉鎖期間中フラグ',
    'deleted': u'削除フラグ',
    }

def timedelta_to_int(td):
    return td.days * 86400 + td.seconds

class ReportMailSender(object):
    def __init__(self, registry, template_path, report_mail_recipients, report_mail_sender, report_mail_subject, now_getter=datetime.now):
        self.registry = registry
        self.template_path = template_path
        self.report_mail_recipients = report_mail_recipients
        self.report_mail_sender = report_mail_sender
        self.report_mail_subject = report_mail_subject
        self.now_getter = now_getter

    def get_mailer(self):
        return Mailer(self.registry.settings)

    def render_body(self, **kwds):
        from xml.sax.saxutils import unescape
        return unescape(render(self.template_path, kwds))

    def render_subject(self, now):
        report_mail_subject = self.report_mail_subject
        if isinstance(report_mail_subject, unicode):
            report_mail_subject = report_mail_subject.encode('utf-8')
        return now.strftime(report_mail_subject).decode('utf-8')

    def __call__(self, num_records, errors):
        now = self.now_getter()
        mailer = self.get_mailer()
        mailer.create_message(
            sender=self.report_mail_sender,
            recipient=', '.join(self.report_mail_recipients),
            subject=self.render_subject(now),
            body=self.render_body(
                now=now,
                num_records=num_records,
                num_errors=len(errors),
                errors=(
                    dict(
                        line=i,
                        localized_field_name=localized_field_names[error.field],
                        message=error.message
                        )
                    for i, errors_for_row in errors
                    for error in errors_for_row
                    )
                )
            )
        mailer.send(self.report_mail_sender, self.report_mail_recipients)


class ShopMasterProcessor(object):
    unmarshaller_factory = make_unmarshaller

    def __init__(self, session, encoding, reporter=None):
        self.session = session
        self.encoding = encoding
        self.reporter = reporter

    def __call__(self, path):
        logger.info('processing %s...' % path)
        from ..models import FamiPortShop

        errors_for_row = [None] 
        def handle_exception(exc_info):
            if issubclass(exc_info[0], MarshalErrorBase):
                errors_for_row[0] = exc_info[1].errors
            else:
                return True

        errors = []
        try:
            with open(path) as f:
                unmarshaller = make_unmarshaller(f, encoding=self.encoding, exc_handler=handle_exception)
                i = 0
                while True:
                    logger.info('reading line %d' % (i + 1))
                    errors_for_row[0] = None
                    try:
                        row = unmarshaller.next()
                    except StopIteration:
                        break
                    i += 1
                    if errors_for_row[0] is not None:
                        logger.info('error: %s' % errors_for_row[0])
                        errors.append((i, errors_for_row[0]))
                        continue
                    logger.info('importing line %d (shop_code: %s)' % (i, row['shop_code']))
                    try:
                        shop = self.session.query(FamiPortShop).filter_by(code=row['shop_code']).one()
                    except NoResultFound:
                        shop = None
                    if shop is None:
                        shop = FamiPortShop(
                            code=row['shop_code'],
                            company_code=row['company_code'],
                            company_name=row['company_name'],
                            district_code=row['district_code'],
                            district_name=row['district_name'],
                            district_valid_from=row['district_valid_from'],
                            branch_code=row['branch_code'],
                            branch_name=row['branch_name'],
                            branch_valid_from=row['branch_valid_from'],
                            name=row['shop_name'],
                            name_kana=row['shop_name_kana'],
                            tel=row['shop_tel'],
                            prefecture=row['prefecture_code'],
                            prefecture_name=row['prefecture_name'],
                            address=row['shop_address'],
                            open_from=row['shop_open_from'],
                            zip=row['zip'],
                            business_run_from=row['business_run_from'],
                            open_at=row['shop_open_at'],
                            close_at=row['shop_close_at'],
                            business_hours=timedelta_to_int(row['business_hours']) if row['business_hours'] else None,
                            opens_24hours=row['opens_24hours'],
                            closest_station=row['closest_station'],
                            liquor_available=row['liquor_available'],
                            cigarettes_available=row['cigarettes_available'],
                            business_run_until=row['business_run_until'],
                            open_until=row['shop_open_until'],
                            business_paused_at=row['business_paused_at'],
                            business_continued_at=row['business_continued_at'],
                            latitude=row['latitude'],
                            longitude=row['longitude'],
                            atm_available=row['atm_available'],
                            atm_available_from=row['atm_available_from'],
                            atm_available_until=row['atm_available_until'],
                            mmk_available=row['mmk_available'],
                            mmk_available_from=row['mmk_available_from'],
                            mmk_available_until=row['mmk_available_until'],
                            renewal_start_at=row['renewal_start_at'],
                            renewal_end_at=row['renewal_end_at'],
                            business_status=row['status'],
                            paused=row['paused'],
                            deleted=row['deleted']
                            )
                        self.session.add(shop)
                    else:
                        if row['company_code_updated'] != 0:
                            shop.company_code = row['company_code']
                        if row['company_name_updated'] != 0:
                            shop.company_name = row['company_name']
                        if row['district_code_updated'] != 0:
                            shop.district_code = row['district_code']
                        if row['district_name_updated'] != 0:
                            shop.district_name = row['district_name']
                        if row['district_valid_from_updated'] != 0:
                            shop.district_valid_from = row['district_valid_from']
                        if row['branch_code_updated'] != 0:
                            shop.branch_code = row['branch_code']
                        if row['branch_name_updated'] != 0:
                            shop.branch_name = row['branch_name']
                        if row['branch_valid_from_updated'] != 0:
                            shop.branch_valid_from = row['branch_valid_from']
                        if row['shop_name_updated'] != 0:
                            shop.name = row['shop_name']
                        if row['shop_name_kana_updated'] != 0:
                            shop.name_kana = row['shop_name_kana']
                        if row['shop_tel_updated'] != 0:
                            shop.tel = row['shop_tel']
                        if row['prefecture_code_updated'] != 0:
                            shop.prefecture = row['prefecture_code']
                        if row['prefecture_name_updated'] != 0:
                            shop.prefecture_name = row['prefecture_name']
                        if row['shop_address_updated'] != 0:
                            shop.address = row['shop_address']
                        if row['shop_open_from_updated'] != 0:
                            shop.open_from = row['shop_open_from']
                        if row['zip_updated'] != 0:
                            shop.zip = row['zip']
                        if row['business_run_from_updated'] != 0:
                            shop.business_run_from = row['business_run_from']
                        if row['shop_open_at_updated'] != 0:
                            shop.open_at = row['shop_open_at']
                        if row['shop_close_at_updated'] != 0:
                            shop.close_at = row['shop_close_at']
                        if row['business_hours_updated'] != 0:
                            shop.business_hours = timedelta_to_int(row['business_hours'])
                        if row['opens_24hours_updated'] != 0:
                            shop.opens_24hours = row['opens_24hours']
                        if row['closest_station_updated'] != 0:
                            shop.closest_station = row['closest_station']
                        if row['liquor_available_updated'] != 0:
                            shop.liquor_available = row['liquor_available']
                        if row['cigarettes_available_updated'] != 0:
                            shop.cigarettes_available = row['cigarettes_available']
                        if row['business_run_until_updated'] != 0:
                            shop.business_run_until = row['business_run_until']
                        if row['shop_open_until_updated'] != 0:
                            shop.open_until = row['shop_open_until']
                        if row['business_paused_at_updated'] != 0:
                            shop.business_paused_at = row['business_paused_at']
                        if row['business_continued_at_updated'] != 0:
                            shop.business_continued_at = row['business_continued_at']
                        if row['latitude_updated'] != 0:
                            shop.latitude = row['latitude']
                        if row['longitude_updated'] != 0:
                            shop.longitude = row['longitude']
                        if row['atm_available_updated'] != 0:
                            shop.atm_available = row['atm_available']
                        if row['atm_available_from_updated'] != 0:
                            shop.atm_available_from = row['atm_available_from']
                        if row['atm_available_until_updated'] != 0:
                            shop.atm_available_until = row['atm_available_until']
                        if row['mmk_available_updated'] != 0:
                            shop.mmk_available = row['mmk_available']
                        if row['mmk_available_from_updated'] != 0:
                            shop.mmk_available_from = row['mmk_available_from']
                        if row['mmk_available_until_updated'] != 0:
                            shop.mmk_available_until = row['mmk_available_until']
                        if row['renewal_start_at_updated'] != 0:
                            shop.renewal_start_at = row['renewal_start_at']
                        if row['renewal_end_at_updated'] != 0:
                            shop.renewal_end_at = row['renewal_end_at']
                        shop.business_status = row['status']
                        shop.paused = row['paused']
                        shop.deleted = row['deleted']
            self.session.commit()
            logger.info('done processing %s (records=%d, errors=%d)' % (path, i, len(errors)))
            if self.reporter is not None:
                self.reporter(
                    num_records=i,
                    errors=errors
                    )
        except Exception:
            exc_info = sys.exc_info()
            self.session.rollback()
            raise exc_info[1], None, exc_info[2]
        return None
        

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv[1:])

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    settings = registry.settings
    pending_dir = settings['altair.famiport.mdm.shop_master.pending_dir']
    imported_dir = settings['altair.famiport.mdm.shop_master.imported_dir']
    encoding = settings.get('altair.famiport.mdm.shop_master.encoding', 'CP932')
    report_mail_recipients = settings.get('altair.famiport.mdm.shop_master.report_mail.recipients')
    if report_mail_recipients is not None:
        report_mail_recipients = [report_mail_recipient.strip() for report_mail_recipient in report_mail_recipients.split(',')]
    else:
        report_mail_recipients = []
    report_mail_sender = settings.get('altair.famiport.mdm.shop_master.report_mail.sender')
    report_mail_subject = settings.get('altair.famiport.mdm.shop_master.report_mail.subject')

    session = get_global_db_session(registry, 'famiport')

    processor = ImportSession(
        pending_dir=pending_dir,
        imported_dir=imported_dir,
        file_filter=normal_file_filter,
        processor=ShopMasterProcessor(
            session=session,
            encoding=encoding,
            reporter=(
                ReportMailSender(
                    registry=registry,
                    template_path='altair.app.ticketing.famiport:mail_templates/shop_master_import_report.txt',
                    report_mail_recipients=report_mail_recipients,
                    report_mail_sender=report_mail_sender,
                    report_mail_subject=report_mail_subject
                    )
                if report_mail_recipients
                else None
                )
            ),
        logger=logger
        )
    processor()

if __name__ == u"__main__":
    main(sys.argv)

