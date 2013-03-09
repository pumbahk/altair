# -*- coding:utf-8 -*-
import logging
from wtforms import Form
from wtforms import fields
from wtforms import TextField
from wtforms.validators import Regexp, Length
from ticketing.formhelpers import Translations, Required, JISX0208
from ticketing.core.models import Site, Venue

logger = logging.getLogger(__name__)

class SiteForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        return Translations()

    name = TextField(
        label = u'会場名',
        validators=[
            Required(),
            JISX0208, 
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    sub_name = TextField(
        label = u'会場名補足',
        validators=[
            JISX0208, 
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    zip = TextField(
        label = u'郵便番号',
        validators=[
            JISX0208, 
            Regexp(u'^([0-9]{3}-[0-9]{4})?$', message=u'000-0000形式で入力してください'),
        ]
    )
    prefecture = TextField(
        label = u'都道府県',
        validators=[
            JISX0208, 
            Length(max=10, message=u'10文字以内で入力してください'),
        ]
    )
    city = TextField(
        label = u'市町村',
        validators=[
            JISX0208, 
            Length(max=20, message=u'20文字以内で入力してください'),
        ]
    )
    street = TextField(
        label = u'町名',
        validators=[
            JISX0208, 
            Length(max=20, message=u'20文字以内で入力してください'),
        ]
    )
    address = TextField(
        label = u'番地',
        validators=[
            JISX0208, 
            Length(max=20, message=u'20文字以内で入力してください'),
        ]
    )
    other_address = TextField(
        label = u'続きの住所',
        validators=[
            JISX0208, 
            Length(max=100, message=u'100文字以内で入力してください'),
        ]
    )
    tel_1 = TextField(
        label = u'電話番号1',
        validators=[
            JISX0208, 
            Length(max=32, message=u'32文字以内で入力してください'),
        ]
    )
    tel_2 = TextField(
        label = u'電話番号2',
        validators=[
            JISX0208, 
            Length(max=32, message=u'32文字以内で入力してください'),
        ]
    )
    fax = TextField(
        label = u'FAX番号',
        validators=[
            JISX0208, 
            Length(max=32, message=u'32文字以内で入力してください'),
        ]
    )

    def validate_code(form, field):
        return
