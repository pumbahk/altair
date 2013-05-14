# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField, TextField, BooleanField, SelectField, RadioField, SelectMultipleField
from wtforms.validators import Optional, Length
from altairsite.smartphone.common.const import SalesEnum
from altaircms.genre.searcher import GenreSearcher
from wtforms.widgets.core import HTMLString
from wtforms.widgets import html_params
from altaircms.formhelpers import CheckboxListField
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

class AreaSearchForm(Form):
    area = HiddenField(label='', validators=[Optional()], default="")
    genre_id = HiddenField(label='', validators=[Optional()], default="")
    page = HiddenField(validators=[Optional()],default="1")

class DetailSearchForm(TopSearchForm):

    cond = RadioField(label = '', validators=[Optional()],
        choices=[("intersection", u'全てを含む'), ("union", u'少なくとも１つを含む')], default="intersection", coerce=str)

    prefectures = CheckboxListField('県名', coerce=str, choices=[
              ('hokkaido', u'北海道'), ('aomori', u'青森'), ('iwate', u'岩手'), ('akita', u'秋田'), ('miyagi', u'宮城'), ('yamagata', u'山形'), ('fukushima', u'福島')
            , ('chiba', u'千葉'), ('tokyo', u'東京'), ('kanagawa', u'神奈川'), ('ibaraki', u'茨城'), ('tochigi', u'栃木') ,('gunma', u'群馬'), ('saitama', u'埼玉'), ('yamanashi', u'山梨')
            , ('nagano', u'長野') ,('niigata', u'新潟'), ('gifu', u'岐阜'), ('aichi', u'愛知') ,('mie', u'三重'), ('shizuoka', u'静岡')
            , ('kyoto', u'京都'), ('osaka', u'大阪'), ('hyogo', u'兵庫'), ('shiga', u'滋賀'), ('nara', u'奈良'), ('wakayama', u'和歌山'), ('toyama', u'富山'), ('ishikawa', u'石川'), ('fukui', u'福井')
            , ('hiroshima', u'広島'), ('okayama', u'岡山'), ('tottori', u'鳥取'), ('shimane', u'島根') ,('yamaguchi', u'山口'), ('tokushima', u'徳島'), ('kagawa', u'香川'), ('ehime', u'愛媛'), ('kouchi', u'高知')
            , ('okinawa', u'沖縄'), ('fukuoka', u'福岡'), ('saga', u'佐賀'), ('nagasaki', u'長崎'), ('kumamoto', u'熊本') ,('oita', u'大分'), ('miyazaki', u'宮崎') ,('kagoshima', u'鹿児島')])

    genre_id = SelectField(label='', validators=[Optional()],choices=[], coerce=str)
    sales_segment = RadioField(label = '',validators=[Optional()]
        ,choices=[(0, u'一般販売'), (1, u'先行販売'), (2, u'先行抽選') ],default=0, coerce=int)

    since_year = SelectField(label='', validators=[Optional()], choices=[])
    since_month = SelectField(label='', validators=[Optional()], choices=[])
    since_day = SelectField(label='', validators=[Optional()], choices=[])
    year = SelectField(label='', validators=[Optional()], choices=[])
    month = SelectField(label='', validators=[Optional()], choices=[])
    day = SelectField(label='', validators=[Optional()], choices=[])

    sale_day = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
    sale_end_day = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
    sale_option = BooleanField('I accept the site rules', [Optional()])


    sale = RadioField(label = '', validators=[Optional()],
        choices=[(0, u'販売中'), (1, u'今週販売開始'), (2, u'販売終了間近'), (3, u'まもなく開演のチケット'), (4, u'販売終了した公演も表示する')],
        default=SalesEnum.ON_SALE, coerce=int)

    def create_genre_selectbox(self, request):
        genre_searcher = GenreSearcher(request)
        genres = genre_searcher.root.children

        self.genre_id.choices = []
        self.genre_id.choices.append([0, u'選択なし'])
        for genre in genres:
            self.genre_id.choices.append([genre.id, genre.label])
            for sub_genre in genre.children:
                self.genre_id.choices.append([sub_genre.id, u"┗ " + sub_genre.label])

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


