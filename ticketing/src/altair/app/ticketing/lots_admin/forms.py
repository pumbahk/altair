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

    event = SelectField(
        label=u"イベント",
        validators=[],
        choices=[],
    )

    lot = SelectField(
        label=u"抽選",
        validators=[
            ## 認証方法一覧にあるかって確認はchocesでやってくれるのだろうか
        ],
        choices=[],
    )

    def validate(self):
        status = super(SearchLotEntryForm, self).validate()
        if status:
            if not self.entry_no.data and \
               not self.tel.data and \
               not self.name.data and \
               not self.email.data and \
               not self.entried_from.data and \
               not self.entried_to.data and \
               not self.lot.data and \
               not self.event.data:
                self.entry_no.errors.append(u'条件を1つ以上指定してください')
                status = False
        return status
