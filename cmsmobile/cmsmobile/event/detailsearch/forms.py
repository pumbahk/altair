# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, RadioField, HiddenField
from wtforms.validators import Length
from wtforms.validators import Required, Optional
from cmsmobile.core.const import SalesEnum
from wtforms.validators import ValidationError

class DetailSearchForm(Form):
    word = TextField(
        label = '',
        validators=[
            Length(max=200, message=u'200文字以内で入力してください'),
            ]
    )

    area = SelectField(
        label='',
        validators=[Optional()],
        choices=[(0, u'選択なし'),(1, u'首都圏'),(2, u'近畿'),(3, u'東海'),
                 (4, u'北海道'),(5, u'東北'),(6, u'北関東'),(7, u'甲信越'),
                 (8, u'北陸'),(9, u'中国'),(10, u'四国'),(11, u'九州'),
                 (12, u'沖縄')],
        coerce=int,
    )

    genre = SelectField(
        label='',
        validators=[Optional()],
        choices=[(0, u'選択なし')],
        coerce=int,
    )

    sale = RadioField(
        label = '',
        validators=[Optional()],
        choices=[(SalesEnum.ON_SALE, u'販売中'), (SalesEnum.WEEK_SALE, u'今週販売開始'),
                 (SalesEnum.NEAR_SALE_END, u'販売終了間近')],
        default=SalesEnum.ON_SALE
    )

    sales_segment = RadioField(
        label = '',
        validators=[Optional()],
        choices=[(0, u'一般販売'), (1, u'先行販売') ],
        default=0
    )

    since_year = SelectField(
        label='',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )

    since_month = SelectField(
        label='',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )

    since_day = SelectField(
        label='',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )

    year = SelectField(
        label='',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )

    month = SelectField(
        label='',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )

    day = SelectField(
        label='',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )

    num = HiddenField(#総件数
                      label='',
                      validators=[Optional()],
                      default="0"
    )

    page = HiddenField(#現在ページ
                       label='',
                       validators=[Optional()],
                       default='1',
                       )

    page_num = HiddenField(#総ページ数
                           label='',
                           validators=[Optional()],
                           default="0"
    )
