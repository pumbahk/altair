# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required, NullableTextField, JISX0208, after1900, SelectField
from ticketing.formhelpers import replace_ambiguous
from ticketing.core.models import Venue, Performance, Stock
from ticketing.payments.plugins.sej import DELIVERY_PLUGIN_ID as SEJ_DELIVERY_PLUGIN_ID
from ticketing.core.utils import ApplicableTicketsProducer

PREFECTURE_ORDER = { u'北海道': 1, u'青森県': 2, u'岩手県': 3, u'宮城県': 4, u'秋田県': 5, u'山形県': 6, u'福島県': 7, u'茨城県': 8, u'栃木県': 9, u'群馬県': 10, u'埼玉県': 11, u'千葉県': 12, u'東京都': -10, u'神奈川県': 14, u'新潟県': 15, u'富山県': 16, u'石川県': 17, u'福井県': 18, u'山梨県': 19, u'長野県': 20, u'岐阜県': 21, u'静岡県': 22, u'愛知県': -8, u'三重県': 24, u'滋賀県': 25, u'京都府': 26, u'大阪府': -9, u'兵庫県': 28, u'奈良県': 29, u'和歌山県': 30, u'鳥取県': 31, u'島根県': 32, u'岡山県': 33, u'広島県': 34, u'山口県': 35, u'徳島県': 36, u'香川県': 37, u'愛媛県': 38, u'高知県': 39, u'福岡県': 40, u'佐賀県': 41, u'長崎県': 42, u'熊本県': 43, u'大分県': 44, u'宮崎県': 45, u'鹿児島県': 46, u'沖縄県': 47 }

class PerformanceForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            conditions = {
                'organization_id':kwargs['organization_id'],
                'original_venue_id':None
            }
            # FIXME: 都道府県が正しい順番に並ばないのは何とかならないものか
            venue_by_pref = dict()
            for venue in Venue.filter_by(**conditions).all():
                pref = venue.site.prefecture if venue.site.prefecture!=None and venue.site.prefecture!='' else u'(不明な都道府県)'
                if not pref in venue_by_pref:
                    venue_by_pref[pref] = [ ]
                venue_by_pref[pref].append(
                    (venue.id,venue.name+(' ('+venue.sub_name+')' if (venue.sub_name!=None and venue.sub_name!='') else ''))
                )
            self.venue_id.choices = [
                (pref, tuple(venue_by_pref[pref])) for pref in sorted(venue_by_pref.keys(), key=lambda x:PREFECTURE_ORDER[x] if PREFECTURE_ORDER.has_key(x) else 99)
            ]
            if 'venue_id' in kwargs:
                venue = Venue.get(kwargs['venue_id'])
                self.venue_id.choices.insert(0, (venue.id, u'%s (現在選択されている会場)' % venue.name))

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = TextField(
        label=u'公演名',
        filters=[
            replace_ambiguous,
            ],
        validators=[
            Required(),
            JISX0208, 
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    code = TextField(
        label=u'公演コード',
        validators=[
            Required(),
            Regexp(u'^[a-zA-Z0-9]*$', message=u'英数字のみ入力できます'),
            Length(min=12, max=12, message=u'12文字入力してください'),
        ],
    )
    open_on = DateTimeField(
        label=u'開場',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    start_on = DateTimeField(
        label=u'開演',
        validators=[Required(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_on = DateTimeField(
        label=u'終演',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    venue_id = SelectField(
        label=u'会場',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int,
    )
    redirect_url_pc = NullableTextField(
        label=u'リダイレクト先URL (PC)',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    redirect_url_mobile = NullableTextField(
        label=u'リダイレクト先URL (携帯)',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    original_id = HiddenField(
        validators=[Optional()],
    )

    def validate_start_on(form, field):
        if field.data and form.open_on.data and field.data < form.open_on.data:
            raise ValidationError(u'開場日時より過去の日時は入力できません')

    def validate_end_on(form, field):
        if field.data and form.start_on.data and field.data < form.start_on.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')

    def validate_code(form, field):
        if field.data:
            query = Performance.filter(Performance.code==field.data)
            if form.id and form.id.data:
                query = query.filter(Performance.id!=form.id.data)
            if query.count():
                raise ValidationError(u'既に使用されています')

    def validate_venue_id(form, field):
        if form.id.data:
            performance = Performance.get(form.id.data)
            if field.data != performance.venue.id:
                if performance.public:
                    raise ValidationError(u'既に公開されているため、会場を変更できません')
                stocks = Stock.filter_by(performance_id=performance.id).filter(Stock.stock_type_id!=None).filter(Stock.quantity>0).count()
                if stocks:
                    raise ValidationError(u'この会場で既に配席されている為、会場を変更できません')


class PerformancePublicForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        self.public.data = int(formdata.get('public', 0))

    id = HiddenField(
        label='',
        validators=[Optional()],
    )
    public = HiddenField(
        label='',
        validators=[Required()],
    )

    def validate_public(form, field):
        # 公開する場合のみチェック
        if field.data == 1:
            # 配下の全てのProductItemに券種が紐づいていること
            performance = Performance.get(form.id.data)
            no_ticket_bundles = ''

            has_sej = performance.has_that_delivery(SEJ_DELIVERY_PLUGIN_ID)

            for product_item in performance.product_items:
                if not product_item.ticket_bundle:
                    p = product_item.product
                    if p.sales_segment is not None:
                        no_ticket_bundles += u'<div>販売区分: %s、商品名: %s</div>' % (p.sales_segment.name, p.name)
                elif has_sej:
                    producer = ApplicableTicketsProducer.from_bundle(product_item.ticket_bundle)
                    if not producer.any_exist(producer.sej_only_tickets()):
                        p = product_item.product
                        if p.sales_segment is not None:
                            no_ticket_bundles += u'<div>販売区分: %s、商品名: %s(SEJ券面なし)</div>' % (p.sales_segment.name, p.name)
                    
            if no_ticket_bundles:
                raise ValidationError(u'券面構成が設定されていない商品設定がある為、公開できません %s' % no_ticket_bundles)
