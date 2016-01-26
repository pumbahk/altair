# -*- coding: utf-8 -*-
from ..common.const import SalesEnum
from altaircms.formhelpers import CheckboxListField
from altairsite.search.forms import parse_date, create_close_date

from wtforms import Form
from datetime import datetime
from wtforms import HiddenField, TextField, BooleanField, SelectField, RadioField
from wtforms.validators import Optional, Length

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

    def validate_word(form, field):
        if not field.data:
            raise ValueError(u'検索文字列を入力してください')
        if len(field.data) > 200:
            raise ValueError(u'200文字以内で入力してください')
        return

class GenreSearchForm(TopSearchForm):

    genre_id = HiddenField(label='', validators=[Optional()], default="0")
    sale = SelectField(
        label='',
        validators=[Optional()],
        choices=[
            (SalesEnum.ON_SALE.v, u'すべてのチケット'),
            (SalesEnum.GENRE.v, u'このジャンルで'),
        ],
        default=SalesEnum.GENRE.v, coerce=int)

class AreaSearchForm(Form):
    word = TextField(label = '', validators=[Optional()], default="")
    area = HiddenField(label='', validators=[Optional()], default="")
    genre_id = HiddenField(label='', validators=[Optional()], default="")
    page = HiddenField(validators=[Optional()],default="1")

class HotwordSearchForm(Form):
    hotword_id = HiddenField(label='', validators=[Optional()], default="")
    genre_id = HiddenField(label='', validators=[Optional()], default="")
    page = HiddenField(validators=[Optional()],default="1")

class DetailSearchForm(TopSearchForm):
    # 詳細検索のみ非検索文字列は必須ではない
    word = TextField(label = '', validators=[Optional()])
    cond = SelectField(
        label='',
        validators=[Optional()],
        choices=[
            ("intersection", u'全てを含む'),
            ("union", u'少なくとも１つを含む'),
        ],
        default=SalesEnum.ON_SALE.v, coerce=str)

    pref_hokkaido = CheckboxListField(u'北海道・東北',
            choices=[
                ('all', u'全てON/OFF'), ('hokkaido', u'北海道'), ('aomori', u'青森'), ('iwate', u'岩手'), ('akita', u'秋田'), ('miyagi', u'宮城'), ('yamagata', u'山形'), ('fukushima', u'福島')
            ])
    pref_syutoken = CheckboxListField(u'首都圏・北関東',
            choices=[
                ('all', u'全てON/OFF'), ('tokyo', u'東京'),  ('kanagawa', u'神奈川'), ('chiba', u'千葉'), ('saitama', u'埼玉'), ('ibaraki', u'茨城'), ('tochigi', u'栃木') ,('gunma', u'群馬'),  ('yamanashi', u'山梨')
            ])
    pref_koshinetsu = CheckboxListField(u'甲信越・東海',
            choices=[
                ('all', u'全てON/OFF'), ('nagano', u'長野') ,('niigata', u'新潟'), ('gifu', u'岐阜'), ('aichi', u'愛知') ,('mie', u'三重'), ('shizuoka', u'静岡')
            ])
    pref_kinki = CheckboxListField(u'近畿・北陸',
            choices=[
                ('all', u'全てON/OFF'), ('kyoto', u'京都'), ('osaka', u'大阪'), ('hyogo', u'兵庫'), ('shiga', u'滋賀'), ('nara', u'奈良'), ('wakayama', u'和歌山'), ('toyama', u'富山'), ('ishikawa', u'石川'), ('fukui', u'福井')
            ])
    pref_chugoku = CheckboxListField(u'中国・四国',
            choices=[
                ('all', u'全てON/OFF'), ('hiroshima', u'広島'), ('okayama', u'岡山'), ('tottori', u'鳥取'), ('shimane', u'島根') ,('yamaguchi', u'山口'), ('tokushima', u'徳島'), ('kagawa', u'香川'), ('ehime', u'愛媛'), ('kouchi', u'高知')
            ])
    pref_kyusyu = CheckboxListField(u'九州・沖縄',
            choices=[
                ('all', u'全てON/OFF'), ('okinawa', u'沖縄'), ('fukuoka', u'福岡'), ('saga', u'佐賀'), ('nagasaki', u'長崎'), ('kumamoto', u'熊本') ,('oita', u'大分'), ('miyazaki', u'宮崎') ,('kagoshima', u'鹿児島')
            ])
    genre_music = CheckboxListField(u'音楽', choices=[], validators=[Optional()], coerce=int)
    genre_sports = CheckboxListField(u'スポーツ', choices=[], validators=[Optional()], coerce=int)
    genre_stage = CheckboxListField(u'演劇・ステージ・舞台', choices=[], validators=[Optional()], coerce=int)
    genre_event = CheckboxListField(u'イベント・その他', choices=[], validators=[Optional()], coerce=int)
    sales_segment = CheckboxListField(u'販売区分',
        choices=[
            ("normal", u'一般発売'), ("precedence", u'先行販売'), ("lottery", u'先行抽選')
        ])
    since_year = SelectField(label='', validators=[Optional()], choices=[], default=0)
    since_month = SelectField(label='', validators=[Optional()], choices=[])
    since_day = SelectField(label='', validators=[Optional()], choices=[])
    year = SelectField(label='', validators=[Optional()], choices=[])
    month = SelectField(label='', validators=[Optional()], choices=[])
    day = SelectField(label='', validators=[Optional()], choices=[])
    sale_start = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    sale_end = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    closed_perf = BooleanField(u'販売終了した公演（絞り込み条件）', [Optional()])
    canceled_perf = BooleanField(u'中止した公演（絞り込み条件）', [Optional()])

    def get_event_open(self):
        event_open = self.create_get_event_open()
        since_event_open = self.create_since_event_open()

        if event_open and since_event_open and event_open < since_event_open:
            event_open = self.create_since_event_open()
            since_event_open = self.create_get_event_open()

        event_open = create_close_date(event_open)
        return since_event_open, event_open

    def get_datetime(self, year, month, day):
        date = None
        try:
            date = parse_date(int(year), int(month), int(day))
        except:
            pass
        return date

    def create_since_event_open(self):
        return self.get_datetime(self.since_year.data, self.since_month.data, self.since_day.data)

    def create_get_event_open(self):
        return self.get_datetime(self.year.data, self.month.data, self.day.data)

    def update_form(self, since_event_open, event_open):
        if since_event_open:
            self.since_year.data = str(since_event_open.year)
            self.since_month.data = str(since_event_open.month)
            self.since_day.data = str(since_event_open.day)
        if event_open:
            self.year.data = str(event_open.year)
            self.month.data = str(event_open.month)
            self.day.data = str(event_open.day)
