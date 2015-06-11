# -*- coding:utf-8 -*-

import argparse
import sys
import os
import logging
from datetime import date
from sqlalchemy.orm.exc import NoResultFound
from pyramid.paster import bootstrap, setup_logging
from ..mdm.shop_master import make_unmarshaller
from ..datainterchange.importing import ImportSession, normal_file_filter

logger = logging.getLogger(__name__)

def timedelta_to_int(td):
    return td.days * 86400 + td.seconds

class ShopMasterProcessor(object):
    unmarshaller_factory = make_unmarshaller

    def __init__(self, session, encoding):
        self.session = session
        self.encoding = encoding

    def __call__(self, path):
        logger.info('processing %s...' % path)
        from ..models import FamiPortShop
        try:
            with open(path) as f:
                unmarshaller = make_unmarshaller(f, encoding=self.encoding)
                for row in unmarshaller:
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
                            business_hours=timedelta_to_int(row['business_hours']),
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
                        if row['name_kana_updated'] != 0:
                            shop.name_kana = row['name_kana']
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
                        if row['close_at_updated'] != 0:
                            shop.close_at = row['close_at']
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
            logger.info('done processing %s' % path)
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

    from ..models import _session

    processor = ImportSession(
        pending_dir=pending_dir,
        imported_dir=imported_dir,
        file_filter=normal_file_filter,
        processor=ShopMasterProcessor(session=_session, encoding=encoding),
        logger=logger
        )
    processor()

if __name__ == u"__main__":
    main(sys.argv)

