# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField, TextField, BooleanField, SelectField, RadioField, SelectMultipleField
from altairsite.mobile.core.helper import log_debug, log_info, log_warn, log_exception, log_error
from wtforms.validators import Optional, Length
from altairsite.smartphone.common.const import SalesEnum
from altaircms.formhelpers import CheckboxListField
from datetime import date, datetime

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
    area = HiddenField(label='', validators=[Optional()], default="")
    genre_id = HiddenField(label='', validators=[Optional()], default="")
    page = HiddenField(validators=[Optional()],default="1")

class DetailSearchForm(TopSearchForm):

    cond = RadioField(label = '', validators=[Optional()],
        choices=[("intersection", u'全てを含む'), ("union", u'少なくとも１つを含む')], default="intersection", coerce=str)
    prefecture_hokkaido = CheckboxListField(u'北海道・東北',
            choices=[
                ('all_check', u'全て選択'), ('hokkaido', u'北海道'), ('aomori', u'青森'), ('iwate', u'岩手'), ('akita', u'秋田'), ('miyagi', u'宮城'), ('yamagata', u'山形'), ('fukushima', u'福島')
            ])
    prefecture_syutoken = CheckboxListField(u'首都圏・北関東',
            choices=[
                ('all_check', u'全て選択'), ('tokyo', u'東京'),  ('kanagawa', u'神奈川'), ('chiba', u'千葉'), ('saitama', u'埼玉'), ('ibaraki', u'茨城'), ('tochigi', u'栃木') ,('gunma', u'群馬'),  ('yamanashi', u'山梨')
            ])
    prefecture_koshinetsu = CheckboxListField(u'甲信越・東海',
            choices=[
                ('all_check', u'全て選択'), ('nagano', u'長野') ,('niigata', u'新潟'), ('gifu', u'岐阜'), ('aichi', u'愛知') ,('mie', u'三重'), ('shizuoka', u'静岡')
            ])
    prefecture_kinki = CheckboxListField(u'近畿・北陸',
            choices=[
                ('all_check', u'全て選択'), ('kyoto', u'京都'), ('osaka', u'大阪'), ('hyogo', u'兵庫'), ('shiga', u'滋賀'), ('nara', u'奈良'), ('wakayama', u'和歌山'), ('toyama', u'富山'), ('ishikawa', u'石川'), ('fukui', u'福井')
            ])
    prefecture_chugoku = CheckboxListField(u'中国・四国',
            choices=[
                ('all_check', u'全て選択'), ('hiroshima', u'広島'), ('okayama', u'岡山'), ('tottori', u'鳥取'), ('shimane', u'島根') ,('yamaguchi', u'山口'), ('tokushima', u'徳島'), ('kagawa', u'香川'), ('ehime', u'愛媛'), ('kouchi', u'高知')
            ])
    prefecture_kyusyu = CheckboxListField(u'九州・沖縄',
            choices=[
                ('all_check', u'全て選択'), ('okinawa', u'沖縄'), ('fukuoka', u'福岡'), ('saga', u'佐賀'), ('nagasaki', u'長崎'), ('kumamoto', u'熊本') ,('oita', u'大分'), ('miyazaki', u'宮崎') ,('kagoshima', u'鹿児島')
            ])
    genre_id = SelectField(label='', validators=[Optional()],choices=[], coerce=str)
    sales_segment = RadioField(label = '',validators=[Optional()]
        ,choices=[("normal", u'一般発売'), ("precedence", u'先行販売'), ("lottery", u'先行抽選') ],default="normal", coerce=str)
    since_year = SelectField(label='', validators=[Optional()], choices=[])
    since_month = SelectField(label='', validators=[Optional()], choices=[])
    since_day = SelectField(label='', validators=[Optional()], choices=[])
    year = SelectField(label='', validators=[Optional()], choices=[])
    month = SelectField(label='', validators=[Optional()], choices=[])
    day = SelectField(label='', validators=[Optional()], choices=[])
    sale_start = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    sale_end = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    closed_perf = BooleanField(u'販売終了した公演', [Optional()])
    canceled_perf = BooleanField(u'中止した公演', [Optional()])

    def get_prefectures(self):
        prefectures = []
        prefectures.extend(self.prefecture_hokkaido.data)
        prefectures.extend(self.prefecture_syutoken.data)
        prefectures.extend(self.prefecture_koshinetsu.data)
        prefectures.extend(self.prefecture_kinki.data)
        prefectures.extend(self.prefecture_chugoku.data)
        prefectures.extend(self.prefecture_kyusyu.data)

        while 'all_check' in prefectures:
            prefectures.remove('all_check')

        log_info("get_prefectures", "prefectures=" + ", ".join(prefectures))
        return prefectures

    def get_since_event_open(self):
        since_event_open = None
        try:
            since_event_open = datetime(int(self.since_year.data), int(self.since_month.data), int(self.since_day.data))
        except Exception as e:
            pass
        return since_event_open

    def get_event_open(self):
        event_open = None
        try:
            event_open = datetime(int(self.year.data), int(self.month.data), int(self.day.data))
        except Exception as e:
            pass
        return event_open

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


