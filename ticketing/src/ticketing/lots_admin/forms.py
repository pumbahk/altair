# -*- coding:utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField
from wtforms.validators import Length, Optional
from altair.formhelpers import (
    DateTimeField,
    Max,
    after1900,
    OurDateWidget,
)

class SearchLotEntryForm(Form):
    entry_no = TextField(
        label=u'申込番号',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    tel = TextField(
        label=u'電話番号',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    name = TextField(
        label=u'氏名',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    email = TextField(
        label=u'メールアドレス',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    entried_from = DateTimeField(
        label=u'申込日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateWidget()
    )

    entried_to = DateTimeField(
        label=u'申込日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
            hour=Max,
            minute=Max,
            second=Max
            ),
        widget=OurDateWidget()
    )
    lot = SelectField(
        label=u"抽選",
        validators=[
            ## 認証方法一覧にあるかって確認はchocesでやってくれるのだろうか
        ],
        choices=[],
    )
