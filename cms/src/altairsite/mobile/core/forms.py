# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField, TextField, BooleanField, SelectField
from wtforms.validators import Optional, Length
from .const import SalesEnum

class CommonForm(Form):

    # --- フォーム表示項目
    word = TextField(label = '', validators=[Length(max=200, message=u'200文字以内で入力してください')])
    sale = SelectField(
        label='',
        validators=[Optional()],
        choices=[
            (SalesEnum.ON_SALE.v, u'すべてのチケット'),
            (SalesEnum.WEEK_SALE.v, u'今週発売のチケット'),
            (SalesEnum.SOON_ACT.v, u'まもなく開演のチケット'),
        ],
        default=SalesEnum.ON_SALE.v, coerce=int)

    # --- リンク取得項目
    genre = HiddenField(validators=[Optional()], default="0")
    sub_genre = HiddenField(validators=[Optional()], default="0")
    area = HiddenField(validators=[Optional()], default="0")

    # --- ページング項目
    num = HiddenField(validators=[Optional()], default="0")
    page = HiddenField(validators=[Optional()],default="1")
    page_num = HiddenField(validators=[Optional()], default="0")

    # --- 検索遷移先
    path = HiddenField(validators=[Optional()], default='/search')

    def validate_word(form, field):
        if not field.data:
            raise ValueError(u'検索文字列を入力してください')
        if len(field.data) > 200:
            raise ValueError(u'200文字以内で入力してください')
        return
