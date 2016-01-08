# -*- coding:utf-8 -*-
import sys
import logging
import traceback
import transaction
import StringIO
from datetime import datetime, timedelta
from pyramid.renderers import render_to_response
from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import (
    ReportFrequencyEnum,
    ReportPeriodEnum,
)
from altair.app.ticketing.lots.adapters import (
    LotEntryStatus,
)
from .models import (
    LotEntryReportSetting,
)

logger = logging.getLogger(__name__)


class ReportCondition(object):
    """
    集計期間： limit_from, limit_to
    対象イベント: event_id
    対象抽選: lot
    抽選は現在申込受付中であること

    """
    def __init__(self, setting, now):
        self.lot = setting.lot
        self.setting = setting
        self.now = now

    @property
    def from_date(self):

        if self.setting.frequency == ReportFrequencyEnum.Daily.v[0]:
            # 日単位では本日分のみ
            return self.to_date
        elif self.setting.frequency == ReportFrequencyEnum.Weekly.v[0]:
            # 週単位では本日から7日前からのもの
            return self.now - timedelta(days=7)
        else:
            return self.now  # XXX?

    @property
    def to_date(self):
        if self.setting.period == ReportPeriodEnum.Normal.v[0]:
            return self.now - timedelta(days=1)
        return self.now

    @property
    def limited_from(self):
        from_date = self.from_date
        if self.setting.period == ReportPeriodEnum.Normal.v[0]:
            return from_date.strftime('%Y-%m-%d 00:00')
        return None

    @property
    def limited_to(self):
        to_date = self.to_date
        if self.setting.period == ReportPeriodEnum.Entire.v[0]:
            return to_date.strftime('%Y-%m-%d %H:%M')
        elif self.setting.period == ReportPeriodEnum.Normal.v[0]:
            return to_date.strftime('%Y-%m-%d 23:59')
        return None

    @property
    def need_total(self):
        return self.setting.period != ReportPeriodEnum.Entire.v[0]

    def is_reportable(self):
        lot = self.lot
        # ss = self.lot.sales_segment
        # limited_to = self.limited_to
        # limited_from = self.limited_from
        # to_date = self.to_date
        # from_date = self.from_date

        # 抽選申込期間中
        if not lot.available_on(self.now):
            return False

        return True


class LotEntryReporter(object):
    subject_format = u'[抽選申込状況レポート|{organization_name}] {event_name} - {lot_name}'
    body_template = "altair.app.ticketing:templates/lots_reports/_mail_body.html"

    def __init__(self, sender, mailer, report_setting):
        self.sender = sender
        self.mailer = mailer
        self.report_setting = report_setting

    @property
    def lot(self):
        return self.report_setting.lot

    @property
    def subject(self):
        return self.subject_format.format(
            organization_name=self.lot.organization.name,
            event_name=self.lot.event.title,
            lot_name=self.lot.name,
            )

    def create_report_mail(self, status):
        body = render_to_response(self.body_template,
                                  dict(lot=self.lot,
                                       lot_available=self.lot.available_on(datetime.now()),
                                       lot_status=status))
        return Message(subject=self.subject,
                       recipients=[x.email for x in self.report_setting.recipients],
                       html=body.text,
                       sender=self.sender)

    def send(self):
        # 対象の集計内容をロード
        status = LotEntryStatus(self.lot)
        # メール作成
        message = self.create_report_mail(status)
        # 送信
        self.mailer.send(message)


def send_lot_report_mails(request, sender):
    logger.info("start send_lot_report_mails")
    now = datetime.now()
    settings = LotEntryReportSetting.get_in_term(now)
    logger.info(u"{0} settings".format(len(settings)))
    mailer = get_mailer(request)
    for setting in settings:
        try:
            setting = DBSession.merge(setting)
            cond = ReportCondition(setting, now)
            if not cond.is_reportable():
                logger.info(u"setting {0} is not reportable".format(setting.id))
                continue
            reporter = LotEntryReporter(sender, mailer, setting)
            logger.info(u"send report setting by id={0}".format(setting.id))
            reporter.send()
            transaction.commit()
        except Exception:
            exc_info = sys.exc_info()
            out = StringIO.StringIO()
            traceback.print_exception(*exc_info, file=out)
            tb = out.getvalue()
            logger.error("error on send_lot_report_mails \n{0}".format(tb))

    logger.info("end send_lot_report_mails")
