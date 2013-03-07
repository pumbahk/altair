# -*- coding: utf-8 -*-

from wtforms import SelectField, RadioField, HiddenField
from wtforms.validators import Required, Optional
from cmsmobile.core.const import SalesEnum
from cmsmobile.event.search.forms import SearchForm

class DetailSearchForm(SearchForm):

    # --- 詳細検索用
    area = SelectField(label='', validators=[Optional()],coerce=int,
        choices=[(0, u'選択なし'),(1, u'首都圏'),(2, u'近畿'),(3, u'東海'),(4, u'北海道'),(5, u'東北'),
                 (6, u'北関東'),(7, u'甲信越'),(8, u'北陸'),(9, u'中国'),(10, u'四国'),(11, u'九州'),(12, u'沖縄')],)
    genre = SelectField(label='', validators=[Optional()],choices=[(0, u'選択なし')], coerce=int)
    sale = RadioField(label = '', validators=[Optional()],
        choices=[(SalesEnum.ON_SALE, u'販売中'), (SalesEnum.WEEK_SALE, u'今週販売開始'),
                 (SalesEnum.NEAR_SALE_END, u'販売終了間近')],
        default=SalesEnum.ON_SALE)
    sales_segment = RadioField(label = '',validators=[Optional()]
        ,choices=[(0, u'一般販売'), (1, u'先行販売') ],default=0)
    since_year = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
    since_month = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
    since_day = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
    year = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
    month = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
    day = SelectField(label='', validators=[Optional()], choices=[], coerce=int)
