# -*- coding:utf-8 -*-

import logging
import transaction
import argparse
from sqlalchemy import Column, ForeignKey, and_
from sqlalchemy.types import String
from sqlalchemy.orm import join, relationship

from pyramid.paster import bootstrap, setup_logging
from altair.app.ticketing.models import DBSession, Identifier
from altair.app.ticketing.core.models import ReportSetting, ReportRecipient
from altair.app.ticketing.operators.models import Operator

logger = logging.getLogger(__name__)


def report_recipient_migration():
    ''' Operator/ReportSetting から ReportRecipient へname/emailをデータ移行
    '''

    tran = transaction.begin()
    try:
        # Operator -> ReportRecipient
        operators = Operator.query.join(ReportSetting).all()
        for o in operators:
            params = dict(name=o.name, email=o.email, organization_id=o.organization_id)
            count = ReportRecipient.query.filter_by(**params).count()
            if count == 0:
                recipient = ReportRecipient(**params)
            elif count == 1:
                recipient = ReportRecipient.query.filter_by(**params).one()
            else:
                raise Exception(u'multiple rows found {}'.format(email))
            for s in o.report_setting:
                recipient.settings.append(s)
            DBSession.merge(recipient)

        # ReportSetting -> ReportRecipient
        settings = ReportSetting.query.filter(ReportSetting.email!=None).all()
        for s in settings:
            if not s.email:
                continue
            for email in s.email.split(','):
                if s.event_id:
                    params = dict(name=s.name, email=email, organization_id=s.event.organization_id)
                elif s.performance_id:
                    params = dict(name=s.name, email=email, organization_id=s.performance.event.organization_id)
                count = ReportRecipient.query.filter_by(**params).count()
                if count == 0:
                    recipient = ReportRecipient(**params)
                elif count == 1:
                    recipient = ReportRecipient.query.filter_by(**params).one()
                else:
                    raise Exception(u'multiple rows found {}'.format(email))
                recipient.settings.append(s)
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
    report_recipient_migration()
    logger.info('end migration')
