# -*- coding: utf-8 -*-

import logging
from .const import SalesKindEnum, SalesTermEnum

from altair.formhelpers import (
    OurForm,
)
from altair.formhelpers.fields import (
    BugFreeSelectMultipleField,
)
from altair.formhelpers.fields import OurSelectField
from altair.formhelpers.widgets import (
    CheckboxMultipleSelect,
)
from wtforms.validators import Optional

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
        choices=[(u'sales_start', u"販売開始日"), (u'lots_announce_time', u"抽選結果発表予定日")]
        )
    sales_term = OurSelectField(
        label=u"期間",
        validators=[Optional()],
        choices=[
            (u"today", u"今日"),
            (u"tomorrow", u"明日"),
            (u"this_week", u"今週（月〜日）"),
            (u"this_week_plus_monday", u"今週（月〜月）"),
            (u"next_week", u"来週（月〜日）"),
            (u"next_week_plus_monday", u"来週（月〜月）"),
            (u"this_month", u"今月"),
            (u"term", u"期間指定"),
        ]
    )
    salessegment_group_kind = BugFreeSelectMultipleField(
        label=u'販売区分',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        choices=[
            ('normal', u'一般発売'),
            ('early_lottery', u'先行抽選'),
            ('early_firstcome', u'先行先着')
        ],
        coerce=str,
    )
    operators = BugFreeSelectMultipleField(
        label=u'担当',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        coerce=str,
    )


