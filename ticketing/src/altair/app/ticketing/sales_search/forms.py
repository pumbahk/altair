# -*- coding: utf-8 -*-

import logging

from altair.app.ticketing.core.models import SalesSegmentKindEnum
from altair.formhelpers import Max, after1900, OurForm
from altair.formhelpers.fields import DateTimeField, OurSelectField, BugFreeSelectMultipleField
from altair.formhelpers.widgets import OurDateTimeWidget, CheckboxMultipleSelect
from wtforms.validators import Optional, Required

from .const import SalesKindEnum, SalesTermEnum

logger = logging.getLogger(__name__)


class SalesSearchForm(OurForm):
    """
    販売日程管理検索のフォーム

    Attributes
    ----------
    sales_kind : OurSelectField
        一般発売か、抽選かのプルダウン
    sales_term : OurSelectField
        検索期間のプルダウン
    salessegment_group_kind : BugFreeSelectMultipleField
        販売区分の種別のチェックボックス
        1. 一般発売
            一般発売、追加発売、当日券、関係者、窓口販売、その他
        2. 先行抽選
            先行抽選、追加抽選、最速抽選
        3. 先行先着
            先行先着
    operators : BugFreeSelectMultipleField
        販売日程管理検索で使用するオペレータ
        営業担当と登録担当どちらも検索対象となる
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        Parameters
        ----------
        formdata : NestedMultiDict
            フォームデータ
        obj : object
            オブジェクト
        prefix : unicode
            prefix
        kwargs : dict
            可変長変数
        """
        super(SalesSearchForm, self).__init__(formdata, obj, prefix, **kwargs)
        if "sales_report_operators" in kwargs:
            self.operators.choices = kwargs['sales_report_operators']

    sales_kind = OurSelectField(
        label=u"検索区分",
        validators=[Optional()],
        choices=[(SalesKindEnum.SALES_START.v, u"販売開始日"), (SalesKindEnum.LOTS_ANNOUNCE_TIME.v, u"抽選結果発表予定日")]
    )
    sales_term = OurSelectField(
        label=u"期間",
        validators=[Required()],
        choices=[
            (SalesTermEnum.TODAY.v, u"今日"),
            (SalesTermEnum.TOMORROW.v, u"明日"),
            (SalesTermEnum.THIS_WEEK.v, u"今週（月〜日）"),
            (SalesTermEnum.THIS_WEEK_PLUS_MONDAY.v, u"今週（月〜月）"),
            (SalesTermEnum.NEXT_WEEK.v, u"来週（月〜日）"),
            (SalesTermEnum.NEXT_WEEK_PLUS_MONDAY.v, u"来週（月〜月）"),
            (SalesTermEnum.THIS_MONTH.v, u"今月"),
            (SalesTermEnum.TERM.v, u"期間指定"),
        ]
    )
    term_from = DateTimeField(
        label=u'公演日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateTimeWidget()
    )
    term_to = DateTimeField(
        label=u'公演日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
            hour=Max,
            minute=Max,
            second=Max,
        ),
        widget=OurDateTimeWidget()
    )
    salessegment_group_kind = BugFreeSelectMultipleField(
        label=u'販売区分',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        choices=[
            (SalesSegmentKindEnum.normal.k, u'一般発売'),
            (SalesSegmentKindEnum.early_lottery.k, u'先行抽選'),
            (SalesSegmentKindEnum.early_firstcome.k, u'先行先着')
        ],
        coerce=str,
    )
    operators = BugFreeSelectMultipleField(
        label=u'担当',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        coerce=str,
    )
