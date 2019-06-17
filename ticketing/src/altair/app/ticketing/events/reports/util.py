# encoding: utf-8
from altair.app.ticketing.core.models import DateCalculationBase
from altair.viewhelpers.datetime_ import create_date_time_formatter

class DateTimeFormatter(object):
    WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
    DATE_FORMAT = u"%Y年%-m月%-d日"
    TIME_FORMAT = u'%-H:%M'

    def format_datetime(self, dt):
        return dt.strftime(self.DATE_FORMAT.encode("utf-8")).decode("utf-8") +\
            u'(%s)' % self.WEEK[dt.weekday()] + \
            dt.strftime(self.TIME_FORMAT.encode("utf-8")).decode("utf-8")

    def format_datetime_for_sheet_name(self, dt):
        format = u"%Y.%m.%d-%H%M%S"
        return dt.strftime(format.encode("utf-8")).decode("utf-8")

    def format_date(self, d):
        format = self.DATE_FORMAT
        return d.strftime(format.encode("utf-8")).decode("utf-8") + u'(%s)' % self.WEEK[d.weekday()]

    def format_time(self, t):
        format =self.TIME_FORMAT
        return t.strftime(format.encode("utf-8")).decode("utf-8")

class DateTimeHelperAdapter(object):

    def format_issuing_start_at(self, pdmp):
        if pdmp.issuing_start_day_calculation_base == DateCalculationBase.Absolute.v:
            if pdmp.issuing_start_at is not None:
                return create_date_time_formatter(self.request).format_datetime(pdmp.issuing_start_at, with_weekday=True)
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.OrderDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'購入日'
                elif pdmp.issuing_interval_days > 0:
                    return u'購入から%d日後' % pdmp.issuing_interval_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'購入日時'
                elif pdmp.issuing_interval_days > 0:
                    return u'購入日時から%d日後' % pdmp.issuing_interval_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.PerformanceStartDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'公演開始日'
                elif pdmp.issuing_interval_days > 0:
                    return u'公演開始から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'公演開始の%d日前' % -pdmp.issuing_interval_days
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.PerformanceEndDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'公演終了日'
                elif pdmp.issuing_interval_days > 0:
                    return u'公演終了から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'公演終了の%d日前' % -pdmp.issuing_interval_days
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.SalesStartDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'販売開始日'
                elif pdmp.issuing_interval_days > 0:
                    return u'販売開始から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'販売開始の%d日前' % -pdmp.issuing_interval_days
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.SalesEndDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'販売終了日'
                elif pdmp.issuing_interval_days > 0:
                    return u'販売終了から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'販売終了の%d日前' % -pdmp.issuing_interval_days
        return u'未設定'

    def format_issuing_end_at(self, pdmp):
        if pdmp.issuing_end_day_calculation_base == DateCalculationBase.Absolute.v:
            if pdmp.issuing_end_at is not None:
                return create_date_time_formatter(self.request).format_datetime(pdmp.issuing_end_at, with_weekday=True)
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.OrderDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'購入日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'購入から%d日後' % pdmp.issuing_end_in_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'購入日時'
                elif pdmp.issuing_end_in_days > 0:
                    return u'購入日時から%d日後' % pdmp.issuing_end_in_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.PerformanceStartDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'公演開始日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'公演開始から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'公演開始の%d日前' % -pdmp.issuing_end_in_days
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.PerformanceEndDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'公演終了日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'公演終了から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'公演終了の%d日前' % -pdmp.issuing_end_in_days
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.SalesStartDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'販売開始日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'販売開始から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'販売開始の%d日前' % -pdmp.issuing_end_in_days
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.SalesEndDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'販売終了日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'販売終了から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'販売終了の%d日前' % -pdmp.issuing_end_in_days
        return u'未設定'

    def format_payment_due_at(self, pdmp):
        if pdmp.payment_due_day_calculation_base == DateCalculationBase.Absolute.v:
            if pdmp.payment_due_at is not None:
                return create_date_time_formatter(self.request).format_datetime(pdmp.payment_due_at, with_weekday=True)
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.OrderDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'購入日'
                elif pdmp.payment_period_days > 0:
                    return u'購入から%d日後' % pdmp.payment_period_days
                else:
                    return u'不正な値'
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'購入日時'
                elif pdmp.payment_period_days > 0:
                    return u'購入日時から%d日後' % pdmp.payment_period_days
                else:
                    return u'不正な値'
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.PerformanceStartDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'公演開始日'
                elif pdmp.payment_period_days > 0:
                    return u'公演開始から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'公演開始の%d日前' % -pdmp.payment_period_days
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.PerformanceEndDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'公演終了日'
                elif pdmp.payment_period_days > 0:
                    return u'公演終了から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'公演終了の%d日前' % -pdmp.payment_period_days
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.SalesStartDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'販売開始日'
                elif pdmp.payment_period_days > 0:
                    return u'販売開始から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'販売開始の%d日前' % -pdmp.payment_period_days
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.SalesEndDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'販売終了日'
                elif pdmp.payment_period_days > 0:
                    return u'販売終了から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'販売終了の%d日前' % -pdmp.payment_period_days
        return u'未設定'
