# -*- coding: utf-8 -*-

from .api import get_no_ticket_bundles

from datetime import datetime, timedelta
from wtforms import Form
from wtforms import TextField, HiddenField, TextAreaField, BooleanField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from altair.formhelpers import Translations, Required, NullableTextField, JISX0208, after1900
from altair.formhelpers.form import OurForm
from altair.formhelpers.filters import zero_as_none
from altair.formhelpers.fields import OurIntegerField, DateTimeField, OurGroupedSelectField, OurSelectField, OurBooleanField
from altair.formhelpers import replace_ambiguous
from altair.app.ticketing.core.models import Site, Venue, Performance, PerformanceSetting, Stock, SalesSegment
from altair.app.ticketing.payments.plugins.sej import DELIVERY_PLUGIN_ID as SEJ_DELIVERY_PLUGIN_ID
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.helpers import label_text_for

PREFECTURE_ORDER = {u'北海道': 1, u'青森県': 2, u'岩手県': 3, u'宮城県': 4, u'秋田県': 5, u'山形県': 6, u'福島県': 7, u'茨城県': 8, u'栃木県': 9, u'群馬県': 10, u'埼玉県': 11, u'千葉県': 12, u'東京都': -10, u'神奈川県': 14, u'新潟県': 15, u'富山県': 16, u'石川県': 17, u'福井県': 18, u'山梨県': 19, u'長野県': 20, u'岐阜県': 21, u'静岡県': 22, u'愛知県': -8,
                    u'三重県': 24, u'滋賀県': 25, u'京都府': 26, u'大阪府': -9, u'兵庫県': 28, u'奈良県': 29, u'和歌山県': 30, u'鳥取県': 31, u'島根県': 32, u'岡山県': 33, u'広島県': 34, u'山口県': 35, u'徳島県': 36, u'香川県': 37, u'愛媛県': 38, u'高知県': 39, u'福岡県': 40, u'佐賀県': 41, u'長崎県': 42, u'熊本県': 43, u'大分県': 44, u'宮崎県': 45, u'鹿児島県': 46, u'沖縄県': 47}


class PerformanceForm(OurForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(PerformanceForm, self).__init__(formdata, obj, prefix, **kwargs)

        self.event = None
        if 'event' in kwargs:
            self.event = kwargs['event']

        if 'organization_id' in kwargs:
            venue_by_pref = dict()
            venues = Venue.query.join(Site).filter(
                Venue.organization_id == kwargs['organization_id'],
                Venue.original_venue_id == None,
                Site.visible == True
            ).with_entities(
                Venue.id, Venue.name, Venue.sub_name, Site.prefecture
            ).order_by(Venue.name, Venue.sub_name).all()

            for id, name, sub_name, prefecture in venues:
                if prefecture is None:
                    perfecture = u'(不明な都道府県)'
                if not prefecture in venue_by_pref:
                    venue_by_pref[prefecture] = []
                if sub_name is not None and sub_name != '':
                    name = u'{0} ({1})'.format(name, sub_name)
                venue_by_pref[prefecture].append((id, name))

            choices = [
                (pref, tuple(venue_by_pref[pref]))
                for pref in sorted(venue_by_pref.keys(), key=lambda x:PREFECTURE_ORDER[x] if PREFECTURE_ORDER.has_key(x) else 99)
            ]
            if 'venue_id' in kwargs:
                venue = Venue.query.get(kwargs['venue_id'])
                choices.insert(
                    0, (None, [(venue.id, u'%s (現在選択されている会場)' % venue.name)]))
            self.venue_id.choices = choices

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
        label=u'公演コード(英数字12桁)',
        validators=[
            Required(),
            Regexp(u'^[a-zA-Z0-9]*$', message=u'半角英数字のみ入力できます'),
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
    venue_id = OurGroupedSelectField(
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

    abbreviated_title = NullableTextField(
        label=u'公演名略称',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    subtitle = NullableTextField(
        label=u'公演名副題',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    note = NullableTextField(
        label=u'公演名備考',
    )
    order_limit = OurIntegerField(
        label=label_text_for(PerformanceSetting.order_limit),
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    entry_limit = OurIntegerField(
        label=label_text_for(PerformanceSetting.entry_limit),
        default=None,
        filters=[zero_as_none],
        validators=[Optional()],
        help=u'この公演に抽選申込できる上限数'
    )
    max_quantity_per_user = OurIntegerField(
        label=label_text_for(PerformanceSetting.max_quantity_per_user),
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    display_order = OurIntegerField(
        label=label_text_for(Performance.display_order),
        default=1,
        hide_on_new=True,
    )

    visible = OurBooleanField(
        label=u'パフォーマンスの表示/非表示',
        default=True,
    )

    def validate_start_on(form, field):
        if field.data and form.open_on.data and field.data < form.open_on.data:
            raise ValidationError(u'開場日時より過去の日時は入力できません')

        # コンビニ発券開始日時をチェックする
        if field.data is not None:
            from altair.app.ticketing.events.sales_segments.forms import validate_issuing_start_at
            from altair.app.ticketing.events.sales_segments.exceptions import IssuingStartAtOutTermException
            performance_start_on = form.start_on.data or field.data
            performance_end_on = form.end_on.data or field.data
            targets = []
            if form.id.data:
                sales_segments = SalesSegment.query.filter_by(
                    performance_id=form.id.data).all()
                for ss in sales_segments:
                    ssg = ss.sales_segment_group
                    if not ss.use_default_start_at:
                        # デフォルト値を使わないケース
                        ss_start_at = ss.start_at
                    else:
                        # SalesSegmentGroupの値を使うケース
                        if not ssg.start_at:
                            s = field.data
                            ss_start_at = datetime(
                                s.year, s.month, s.day, ssg.start_time.hour, ssg.start_time.minute)
                            ss_start_at -= timedelta(
                                days=ssg.start_day_prior_to_performance)
                        else:
                            assert ss.start_at == ssg.start_at
                            ss_start_at = ssg.start_at
                    if not ss.use_default_end_at:
                        # デフォルト値を使わないケース
                        ss_end_at = ss.end_at
                    else:
                        # SalesSegmentGroupの値を使うケース
                        if not ssg.end_at:
                            # で、かつ相対指定の場合
                            s = field.data
                            ss_end_at = datetime(
                                s.year, s.month, s.day, ssg.end_time.hour, ssg.end_time.minute)
                            ss_end_at -= timedelta(
                                days=ssg.end_day_prior_to_performance)
                        else:
                            # 絶対指定の場合
                            assert ss.end_at == ssg.end_at
                            ss_end_at = ssg.end_at
                    targets.append(
                        (ss_start_at, ss_end_at, ss.payment_delivery_method_pairs))
            else:
                sales_segment_groups = form.event.sales_segment_groups
                for ssg in sales_segment_groups:
                    if not ssg.start_at:
                        s = field.data
                        ss_start_at = datetime(
                            s.year, s.month, s.day, ssg.start_time.hour, ssg.start_time.minute)
                        ss_start_at -= timedelta(
                            days=ssg.start_day_prior_to_performance)
                    else:
                        ss_start_at = ssg.start_at
                    if not ssg.end_at:
                        s = field.data
                        ss_end_at = datetime(
                            s.year, s.month, s.day, ssg.end_time.hour, ssg.end_time.minute)
                        ss_end_at -= timedelta(
                            days=ssg.end_day_prior_to_performance)
                    else:
                        ss_end_at = ssg.end_at
                    targets.append(
                        (ss_start_at, ss_end_at, ssg.payment_delivery_method_pairs))
            for ss_start_at, ss_end_at, pdmps in targets:
                for pdmp in pdmps:
                    try:
                        validate_issuing_start_at(
                            performance_start_on=performance_start_on,
                            performance_end_on=performance_end_on,
                            sales_segment_start_at=ss_start_at,
                            sales_segment_end_at=ss_end_at,
                            pdmp=pdmp
                        )
                    except IssuingStartAtOutTermException as e:
                        raise ValidationError(e.message)

    def validate_end_on(form, field):
        if field.data and form.start_on.data and field.data < form.start_on.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')

    def validate_code(form, field):
        if field.data:
            query = Performance.filter(Performance.code == field.data)
            if form.id and form.id.data:
                query = query.filter(Performance.id != form.id.data)
            if query.count():
                raise ValidationError(u'既に使用されています')

    def validate_venue_id(form, field):
        if form.id.data:
            performance = Performance.get(form.id.data)
            if field.data != performance.venue.id:
                if performance.public:
                    raise ValidationError(u'既に公開されているため、会場を変更できません')
                stocks = Stock.filter_by(performance_id=performance.id).filter(
                    Stock.stock_type_id != None).filter(Stock.quantity > 0).count()
                if stocks:
                    raise ValidationError(u'この会場で既に配席されている為、会場を変更できません')


class PerformanceManycopyForm(OurForm):
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
    start_on = TextField(
        label=u'開演',
        validators=[Required(), after1900],
    )
    end_on = TextField(
        label=u'終演',
        validators=[Optional(), after1900],
    )
    display_order = OurIntegerField(
        label=label_text_for(Performance.display_order),
        default=1,
        hide_on_new=True,
    )


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
            no_ticket_bundles = get_no_ticket_bundles(performance)
            if no_ticket_bundles:
                raise ValidationError(
                    u'券面構成が設定されていない商品設定がある為、公開できません %s' % no_ticket_bundles)


class OrionPerformanceForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(OrionPerformanceForm, self).__init__(
            formdata, obj, prefix, **kwargs)
        if 'data' in kwargs and kwargs['data'] is not None:
            d = kwargs['data']
            for k in d.__table__.columns:
                if k.name in self:
                    self[k.name].data = getattr(d, k.name)

    enabled = BooleanField(
        label=u'連携する',
        validators=[Optional()],
    )

    web = TextField(
        label=u'Webサイト',
        validators=[Optional()],
    )

    instruction_general = TextAreaField(
        label=u'説明(一般)',
        validators=[Optional()],
    )

    instruction_performance = TextAreaField(
        label=u'説明(公演)',
        validators=[Optional()],
    )

    qr_enabled = BooleanField(
        label=u'QR認証を使う',
        validators=[Optional()],
    )

    pattern = TextField(
        label=u'もぎり認証パターン',
        validators=[Optional()],
    )

    coupon_2_enabled = BooleanField(
        label=u'副券を使う',
        validators=[Optional()],
    )

    coupon_2_name = TextField(
        label=u'[副券] 名称',
        validators=[Optional()],
    )

    coupon_2_qr_enabled = BooleanField(
        label=u'[副券] QR認証を使う',
        validators=[Optional()],
    )

    coupon_2_pattern = TextField(
        label=u'[副券] もぎり認証パターン',
        validators=[Optional()],
    )

    icon_url = TextField(
        label=u'アイコンファイルURL',
        validators=[Optional()],
    )

    header_url = TextField(
        label=u'ヘッダ画像URL',
        validators=[Optional()],
    )

    background_url = TextField(
        label=u'背景画像URL',
        validators=[Optional()],
    )
