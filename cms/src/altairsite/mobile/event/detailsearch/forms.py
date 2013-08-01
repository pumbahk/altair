# -*- coding: utf-8 -*-

from wtforms import SelectField, RadioField, TextField
from wtforms.validators import Optional
from altairsite.mobile.core.const import SalesEnum
from altairsite.mobile.event.search.forms import SearchForm
from altairsite.search.forms import parse_date, create_close_date
from datetime import date
from altairsite.mobile.core.helper import log_info
from altaircms.formhelpers import CheckboxListField

class DetailSearchForm(SearchForm):

    # --- 詳細検索用
    word = TextField(label = '', validators=[Optional()])
    area = SelectField(label='', validators=[Optional()],coerce=int,
        choices=[(0, u'選択なし'),(1, u'首都圏'),(2, u'近畿'),(3, u'東海'),(4, u'北海道'),(5, u'東北'),
                 (6, u'北関東'),(7, u'甲信越'),(8, u'北陸'),(9, u'中国'),(10, u'四国'),(11, u'九州'),(12, u'沖縄')],)
    genre = SelectField(label='', validators=[Optional()],choices=[(0, u'選択なし')], coerce=int)
    sale = RadioField(label = '', validators=[Optional()],
        choices=[(0, u'販売中'), (1, u'今週販売開始'), (2, u'販売終了間近'), (3, u'まもなく開演のチケット'), (4, u'販売終了した公演も表示する')],
        default=SalesEnum.ON_SALE, coerce=int)
    sales_segment = CheckboxListField(u'販売区分',
        choices=[
            ("normal", u'一般発売'), ("precedence", u'先行販売'), ("lottery", u'先行抽選')
        ])
    since_year = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    since_month = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    since_day = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    year = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    month = SelectField(label='', validators=[Optional()], choices=[], coerce=str)
    day = SelectField(label='', validators=[Optional()], choices=[], coerce=str)

    def validate_word(form, field):
        if len(field.data) > 200:
            raise ValueError(u'200文字以内で入力してください')
        return

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
        if year and month and day:
            date = parse_date(int(year), int(month), int(day))
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

