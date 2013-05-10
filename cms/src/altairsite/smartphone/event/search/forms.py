# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField, TextField, BooleanField, SelectField, RadioField
from wtforms.validators import Optional, Length
from altairsite.smartphone.common.const import SalesEnum
from datetime import date

class TopSearchForm(Form):

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
    page = HiddenField(validators=[Optional()],default="1")

class GenreSearchForm(TopSearchForm):

    genre_id = HiddenField(label='', validators=[Optional()], default="0")
    sale = SelectField(
        label='',
        validators=[Optional()],
        choices=[
            (SalesEnum.ON_SALE.v, u'すべてのチケット'),
            (SalesEnum.GENRE.v, u'このジャンルで'),
        ],
        default=SalesEnum.ON_SALE.v, coerce=int)

class DetailSearchForm(Form):

    # --- 詳細検索用
    area = SelectField(label='', validators=[Optional()],coerce=int,
        choices=[(0, u'選択なし'),(1, u'首都圏'),(2, u'近畿'),(3, u'東海'),(4, u'北海道'),(5, u'東北'),
                 (6, u'北関東'),(7, u'甲信越'),(8, u'北陸'),(9, u'中国'),(10, u'四国'),(11, u'九州'),(12, u'沖縄')],)
    genre = SelectField(label='', validators=[Optional()],choices=[(0, u'選択なし')], coerce=int)
    sale = RadioField(label = '', validators=[Optional()],
        choices=[(0, u'販売中'), (1, u'今週販売開始'), (2, u'販売終了間近'), (3, u'まもなく開演のチケット'), (4, u'販売終了した公演も表示する')],
        default=SalesEnum.ON_SALE, coerce=int)
    sales_segment = RadioField(label = '',validators=[Optional()]
        ,choices=[(0, u'一般販売'), (1, u'先行販売'), (2, u'先行抽選') ],default=0, coerce=int)
    since_year = SelectField(label='', validators=[Optional()], choices=[])
    since_month = SelectField(label='', validators=[Optional()], choices=[])
    since_day = SelectField(label='', validators=[Optional()], choices=[])
    year = SelectField(label='', validators=[Optional()], choices=[])
    month = SelectField(label='', validators=[Optional()], choices=[])
    day = SelectField(label='', validators=[Optional()], choices=[])

    def validate_since_year(form, field):

        if form.since_year.data=="0" and form.since_month.data == "0" and form.since_day.data == "0":
            return

        if not _check_date(form.since_year.data, form.since_month.data, form.since_day.data):
            raise ValueError (u'日付が不正です')

        if _check_date(form.year.data, form.month.data, form.day.data):
            since_perf_date = date(
                int(form.since_year.data), int(form.since_month.data), int(form.since_day.data))
            perf_date = date(
                int(form.year.data), int(form.month.data), int(form.day.data))
            if (since_perf_date > perf_date):
                raise ValueError(u'検索範囲が不正です')
        return

    def validate_year(form, field):
        if form.year.data=="0" and form.month.data == "0" and form.day.data == "0":
            return

        if not _check_date(form.year.data, form.month.data, form.day.data):
            raise ValueError (u'日付が不正です')
        return

    def validate_word(form, field):
        if field.data == "":
            raise ValueError(u'検索文字列を入力してください')
        if len(field.data) > 200:
            raise ValueError(u'200文字以内で入力してください')
        return

def _check_date(year, month, day):
    try:
        perf_date = date(int(year), int(month), int(day))
    except ValueError:
        return False
    except TypeError:
        return False
    return True
