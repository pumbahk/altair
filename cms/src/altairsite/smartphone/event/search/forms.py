# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField, TextField, BooleanField, SelectField
from wtforms.validators import Optional, Length
from altairsite.smartphone.common.const import SalesEnum

class SearchForm(Form):

    word = TextField(label = '', validators=[Length(max=200, message=u'200文字以内で入力してください')])
    sale = SelectField(
        label='',
        validators=[Optional()],
        choices=[
            (SalesEnum.ON_SALE.v, u'すべてのチケット'),
            (SalesEnum.GENRE.v, u'このジャンルで'),
            (SalesEnum.WEEK_SALE.v, u'今週発売のチケット'),
            (SalesEnum.SOON_ACT.v, u'まもなく開演のチケット'),
        ],
        default=SalesEnum.ON_SALE.v, coerce=int)
    page = HiddenField(validators=[Optional()],default="1")

class DetailSearchForm(Form):

    word = TextField(label = '', validators=[Length(max=200, message=u'200文字以内で入力してください')])
    sale = SelectField(
        label='',
        validators=[Optional()],
        choices=[
            (SalesEnum.ON_SALE.v, u'すべてのチケット'),
            (SalesEnum.GENRE.v, u'このジャンルで'),
            (SalesEnum.WEEK_SALE.v, u'今週発売のチケット'),
            (SalesEnum.SOON_ACT.v, u'まもなく開演のチケット'),
        ],
        default=SalesEnum.ON_SALE.v, coerce=int)
    page = HiddenField(validators=[Optional()],default="1")
