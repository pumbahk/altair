# -*- coding:utf-8 -*-

import logging
import transaction
import argparse
from sqlalchemy.orm import join

from pyramid.paster import bootstrap, setup_logging
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import ReportRecipient
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.events.lots.models import LotEntryReportSetting

logger = logging.getLogger(__name__)


def execute():
    ''' Operator/LotEntryReportSetting から ReportRecipient へname/emailをデータ移行
    '''

    tran = transaction.begin()
    try:
        # Operator -> ReportRecipient
        operators = Operator.query.join(LotEntryReportSetting).all()
        for o in operators:
            params = dict(name=o.name, email=o.email, organization_id=o.organization_id)
            count = ReportRecipient.query.filter_by(**params).count()
            if count == 0:
                recipient = ReportRecipient(**params)
            elif count == 1:
                recipient = ReportRecipient.query.filter_by(**params).one()
            else:
                raise Exception(u'multiple rows found {}'.format(email))
            for s in o.lot_entry_report_setting:
                recipient.lot_entry_report_settings.append(s)
            DBSession.merge(recipient)

        # LotEntryReportSetting -> ReportRecipient
        settings = LotEntryReportSetting.query.filter(LotEntryReportSetting.email!=None).all()
        for s in settings:
            if not s.email:
                continue
            for email in s.email.split(','):
                params = dict(name=s.name, email=email, organization_id=s.lot.organization_id)
                count = ReportRecipient.query.filter_by(**params).count()
                if count == 0:
                    recipient = ReportRecipient(**params)
                elif count == 1:
                    recipient = ReportRecipient.query.filter_by(**params).one()
                else:
                    raise Exception(u'multiple rows found {}'.format(email))
                recipient.lot_entry_report_settings.append(s)
                DBSession.merge(recipient)

        tran.commit()
    except Exception, e:
        tran.abort()
        logger.exception(e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)

    logger.info('start migration')
    execute()
    logger.info('end migration')
