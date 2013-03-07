# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField, TextField, BooleanField
from wtforms.validators import Optional, Length

class CommonForm(Form):

    # --- フォーム表示項目
    word = TextField(label = '', validators=[Length(max=200, message=u'200文字以内で入力してください')])
    week_sale = BooleanField(label='', validators=[Optional()], default=False)
    soon_act = BooleanField(label='', validators=[Optional()], default=False)

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
