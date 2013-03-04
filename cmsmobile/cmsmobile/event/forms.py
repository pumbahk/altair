# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, BooleanField, SelectField, RadioField, DateField
from wtforms.validators import Length
from wtforms.validators import Optional, ValidationError

class SearchForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

    genre = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )

    sub_genre = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )

    area = HiddenField(
        label='',
        validators=[Optional()],
        default="",
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

    path = HiddenField(
        label='',
        validators=[Optional()],
        default='/search'
    )

    word = TextField(
        label = '',
        validators=[
            Length(max=200, message=u'200文字以内で入力してください'),
            ]
    )

    week_sale = BooleanField(
        label = '',
        validators=[Optional()],
        default=False
    )

    soon_act = BooleanField(
        label = '',
        validators=[Optional()],
        default=False
    )

class HotwordForm(Form):
    id = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )

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
        choices=[(0, u'選択なし'),(1, u'首都圏'),(2, u'近畿'),(3, u'東海'),(4, u'北海道'),(5, u'東北'),
                 (6, u'北関東'),(7, u'甲信越'),(8, u'北陸'),(9, u'中国'),(10, u'四国'),(11, u'九州'),(12, u'沖縄')],
        coerce=int,
    )

    genre = SelectField(
        label='',
        validators=[Optional()],
        choices=[(0, u'選択なし')],
        coerce=int,
    )

    sub_genre = SelectField(
        label='',
        validators=[Optional()],
        choices=[(0, u'選択なし')],
        coerce=int,
    )

    sale = RadioField(
        label = '',
        validators=[Optional()],
        choices=[(u'販売中', u'販売中'), (u'今週販売開始', u'今週販売開始'), (u'販売終了間近', u'販売終了間近')],
        default=u"販売中"
    )

    sales_segment = RadioField(
        label = '',
        validators=[Optional()],
        choices=[(u'一般販売', u'一般販売'), (u'先行販売', u'先行販売') ],
        default=u"一般販売"
    )

    since_year = TextField(
        label = '',
        validators=[]
    )

    since_month = TextField(
        label = '',
        validators=[]
    )

    since_day = TextField(
        label = '',
        validators=[]
    )

    year = TextField(
        label = '',
        validators=[]
    )

    month = TextField(
        label = '',
        validators=[]
    )

    day = TextField(
        label = '',
        validators=[]
    )
