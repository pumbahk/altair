# -*- coding: utf-8 -*-

import locale
from datetime import datetime

from wtforms import Form, ValidationError
from wtforms import (HiddenField, TextField, SelectField, SelectMultipleField, TextAreaField,
                     BooleanField, RadioField, FieldList, FormField, DecimalField, IntegerField)
from wtforms.validators import Optional, AnyOf, Length, Email
from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import (PaymentMethodPlugin, DeliveryMethodPlugin, PaymentMethod,
                                   SalesSegment, Performance, Product, ProductItem, Event)
from ticketing.cart.schemas import ClientForm

class OrderForm(Form):

    def _get_translations(self):
        return Translations()

    order_no = HiddenField(
        label=u'予約番号',
        validators=[Optional()],
    )
    total_amount = HiddenField(
        label=u'合計',
        validators=[Optional()],
    )
    created_at = HiddenField(
        label=u'予約日時',
        validators=[Optional()],
    )
    system_fee = DecimalField(
        label=u'システム利用料',
        places=2,
        default=0,
        validators=[Required()],
    )
    transaction_fee = DecimalField(
        label=u'決済手数料',
        places=2,
        default=0,
        validators=[Required()],
    )
    delivery_fee = DecimalField(
        label=u'配送手数料',
        places=2,
        default=0,
        validators=[Required()],
    )

class OrderSearchForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        if 'event_id' in kwargs:
            event = Event.get(kwargs['event_id'])
            self.event_id.choices = [(event.id, event.title)]
        elif 'organization_id' in kwargs:
            events = Event.filter_by(organization_id=kwargs['organization_id'])
            self.event_id.choices = [('', '')]+[(e.id, e.title) for e in events]

        if 'performance_id' in kwargs:
            performance = Performance.get(kwargs['performance_id'])
            self.performance_id.choices = [(performance.id, performance.name)]
        elif formdata and 'event_id' in formdata:
            performances = Performance.filter_by(event_id=formdata['event_id'])
            self.performance_id.choices = [('', '')]+[(p.id, '%s (%s)' % (p.name, p.start_on.strftime('%Y-%m-%d %H:%M'))) for p in performances]

    order_no = TextField(
        label=u'予約番号',
        validators=[Optional()],
    )
    ordered_from = DateTimeField(
        label=u'予約日時',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    ordered_to = DateTimeField(
        label=u'予約日時',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    payment_method = SelectMultipleField(
        label=u'決済方法',
        validators=[Optional()],
        choices=[(pm.id, pm.name) for pm in PaymentMethodPlugin.all()],
        coerce=int,
    )
    delivery_method = SelectMultipleField(
        label=u'配送方法',
        validators=[Optional()],
        choices=[(pm.id, pm.name) for pm in DeliveryMethodPlugin.all()],
        coerce=int,
    )
    status = SelectMultipleField(
        label=u'ステータス',
        validators=[Optional()],
        choices=[('ordered', u'未入金'), ('paid', u'入金済み'), ('issued', u'発券済み'), ('unissued', u'未発券'), ('delivered', u'配送済み'), ('canceled', u'キャンセル'), ('refunded', u'キャンセル (返金済)')],
        coerce=str,
    )
    name = TextField(
        label=u'氏名',
        validators=[Optional()],
    )
    member_id = TextField(
        label=u'会員番号',
        validators=[Optional()],
    )
    tel = TextField(
        label=u'電話番号',
        validators=[Optional()],
    )
    email = TextField(
        label=u'メールアドレス',
        validators=[Optional()],
    )
    seat_number = TextField(
        label=u'座席番号',
        validators=[Optional()],
    )
    event_id = SelectField(
        label=u"イベント",
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    performance_id = SelectField(
        label=u"公演",
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    start_on_from = DateTimeField(
        label=u'公演日時',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    start_on_to = DateTimeField(
        label=u'公演日時',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    sort = HiddenField(
        validators=[Optional()],
    )
    direction = HiddenField(
        validators=[Optional(), AnyOf(['asc', 'desc'], message='')],
        default='desc',
    )

    def get_conditions(self):
        conditions = {}
        for name, field in self._fields.items():
            if isinstance(field, HiddenField):
                continue
            if not field.data:
                continue

            if isinstance(field, SelectMultipleField) or isinstance(field, SelectField):
                data = []
                for choice in field.choices:
                    if isinstance(field.data, list) and choice[0] in field.data:
                        data.append(choice[1])
                    elif choice[0] == field.data:
                        data.append(choice[1])
                data = ', '.join(data)
            elif isinstance(field, DateTimeField):
                data = field.data.strftime('%Y-%m-%d %H:%M')
            else:
                data = field.data
            conditions[name] = (field.label.text, data)
        return conditions

class PerformanceSearchForm(Form):
    event_id =  HiddenField(
        validators=[Optional()],
    )        
    sort = HiddenField(
        validators=[Optional()],
    )
    direction = HiddenField(
        validators=[Optional(), AnyOf(['asc', 'desc'], message='')],
        default='desc',
    )

class OrderReserveForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'performance_id' in kwargs:
            performance = Performance.get(kwargs['performance_id'])
            self.performance_id.data = performance.id

            now = datetime.now()
            sales_segments = SalesSegment.filter_by(kind='sales_counter')\
                                         .filter_by(event_id=performance.event_id)\
                                         .filter(SalesSegment.start_at<=now)\
                                         .filter(now<=SalesSegment.end_at).all()
            self.payment_delivery_method_pair_id.choices = []
            for sales_segment in sales_segments:
                for pdmp in sales_segment.payment_delivery_method_pairs:
                    self.payment_delivery_method_pair_id.choices.append(
                        (pdmp.id, '%s  -  %s' % (pdmp.payment_method.name, pdmp.delivery_method.name))
                    )

            self.sales_counter_payment_method_id.choices = [(0, '')]
            for pm in PaymentMethod.filter_by_organization_id(performance.event.organization_id):
                self.sales_counter_payment_method_id.choices.append((pm.id, pm.name))

            now = datetime.now()
            self.products.choices = []
            products = []
            if 'stocks' in kwargs and kwargs['stocks']:
                # 座席選択あり
                products = Product.filter(Product.event_id==performance.event_id)\
                                  .join(Product.items)\
                                  .filter(ProductItem.performance_id==performance.id)\
                                  .filter(ProductItem.stock_id.in_(kwargs['stocks'])).all()
            #else:
            #    # 数受け
            #    products = Product.filter(Product.sales_segment_id.in_([ss.id for ss in sales_segments]))\
            #                      .join(Product.seat_stock_type)\
            #                      .filter(StockType.quantity_only==1).all()
            for p in products:
                if p.sales_segment.start_at <= now and p.sales_segment.end_at >= now:
                    self.products.choices += [
                        (p.id, dict(name=p.name, sales_segment=p.sales_segment.name, price=p.price))
                    ]

    def _get_translations(self):
        return Translations()

    performance_id = HiddenField(
        validators=[Required()],
    )
    stocks = HiddenField(
        label='',
        validators=[Optional()],
    )
    note = TextAreaField(
        label=u'備考・メモ',
        validators=[
            Optional(),
            Length(max=2000, message=u'2000文字以内で入力してください'),
        ],
    )
    products = SelectMultipleField(
        label=u'商品',
        validators=[Optional()],
        choices=[],
        coerce=int
    )
    payment_delivery_method_pair_id = SelectField(
        label=u'決済・配送方法',
        validators=[Required(u'決済配送方法を選択してください')],
        choices=[],
        coerce=int
    )
    sales_counter_payment_method_id = SelectField(
        label=u'当日窓口決済',
        validators=[Optional()],
        choices=[],
        coerce=int
    )

    def validate_stocks(form, field):
        if len(field.data) == 0:
            raise ValidationError(u'座席および席種を選択してください')
        if len(field.data) > 1:
            raise ValidationError(u'複数の席種を選択することはできません')
        if not form.products.choices:
            raise ValidationError(u'選択された座席に紐づく予約可能な商品がありません')

class ClientOptionalForm(ClientForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        ClientForm.__init__(self, formdata, obj, prefix, **kwargs)

        # 全てのフィールドをOptionalにする
        for field in self:
            for i, validator in enumerate(field.validators):
                setattr(field.flags, 'required', False)
                if isinstance(validator, Required):
                    del field.validators[i]
                    break;
            field.validators.append(Optional())

class SejTicketForm(Form):
    ticket_type = SelectField(
        label=u'チケット区分',
        choices=[(u'', '-'),(u'1', u'本券（バーコード付き）'), (u'2', u'本券'), (u'3', u' 副券（バーコード付き）'), (u'4', u' 副券')],
        validators=[Optional()],
    )
    event_name              = TextField(
        label=u'イベント名',
        validators=[Required()],
    )
    performance_name        = TextField(
        label=u'パフォーマンス名',
        validators=[Required()],
    )
    performance_datetime    = DateTimeField(
        label=u'発券期限',
        validators=[Optional()],
    )
    ticket_template_id      = TextField(
        label=u'テンプレートID',
        validators=[Required()],
    )
    ticket_data_xml         = TextAreaField(
        label=u'XML',
        validators=[Required()],
    )

class SejOrderForm(Form):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    order_id= TextField(
        label=u'オーダーID',
        validators=[Optional()],
    )
    shop_id= TextField(
        label=u'ショップID',
        default=30520,
        validators=[Optional()],
    )
    shop_name= TextField(
        label=u'ショップ名',
        default=u'楽天チケット',
        validators=[Optional()],
    )
    contact_01= TextField(
        label=u'連絡先１',
        validators=[Optional()],
    )
    contact_02= TextField(
        label=u'連絡先２',
        validators=[Optional()],
    )
    user_name= TextField(
        label=u'ユーザー名',
        validators=[Optional()],
    )
    user_name_kana= TextField(
        label=u'ユーザー名（カナ）',
        validators=[Optional()],
    )
    tel= TextField(
        label=u'ユーザー電話番号',
        validators=[Optional()],
    )
    zip_code= TextField(
        label=u'ユーザー郵便番号',
        validators=[Optional()],
    )
    email= TextField(
        label=u'ユーザーEmail',
        validators=[Optional()],
    )

    total_price = TextField(
        label=u'合計',
        validators=[Required()],
    )
    ticket_price = TextField(
        label=u'チケット金額',
        validators=[Required()],
    )
    commission_fee = TextField(
        label=u'手数料',
        validators=[Required()],
    )
    ticketing_fee = TextField(
        label=u'発券手数料',
        validators=[Required()],
    )

    payment_due_at = DateTimeField(
        label=u'支払い期限',
        validators=[Optional()],
    )
    ticketing_start_at = DateTimeField(
        label=u'発券開始',
        validators=[Optional()],
    )
    ticketing_due_at = DateTimeField(
        label=u'発券期限',
        validators=[Optional()],
    )
    regrant_number_due_at = DateTimeField(
        label=u'SVC再付番期限',
        validators=[Required()],
    )

    payment_type = SelectField(
        label=u'支払い方法',
        choices=[(u'1', u'代引き'), (u'2', u'前払い(後日発券)'), (u'3', u' 代済発券'), (u'4', u' 前払いのみ')],
        validators=[Optional()],
    )

    update_reason = SelectField(
        label=u'更新理由',
        choices=[(u'1', u'項目変更'), (u'2', u'公演中止')],
        validators=[Optional()],
    )

    #tickets = FieldList(FormField(SejTicketForm), min_entries=20)



class SejRefundEventForm(Form):

    available = BooleanField(
        label=u'有効フラグ',
        validators=[Required()],
    )
    shop_id = TextField(
        label=u'ショップID',
        default=30520,
        validators=[Required()],
    )
    event_code_01      = TextField(
        label=u'公演決定キー1	',
        validators=[Required()],
    )
    event_code_02       = TextField(
        label=u'公演決定キー2	',
        validators=[Optional()],
    )
    title      = TextField(
        label=u'メインタイトル',
        validators=[Required()],
    )
    sub_title      = TextField(
        label=u'サブタイトル',
        validators=[Optional()],
    )
    event_at = DateTimeField(
        label=u'公演日',
        validators=[Required()],
    )
    start_at = DateTimeField(
        label=u'レジ払戻受付開始日	',
        validators=[Required()],
    )
    end_at = DateTimeField(
        label=u'レジ払戻受付終了日	',
        validators=[Required()],
    )
    event_expire_at = DateTimeField(
        label=u'公演レコード有効期限	',
        validators=[Required()],
    )
    ticket_expire_at = DateTimeField(
        label=u'チケット持ち込み期限	',
        validators=[Required()],
    )
    refund_enabled = BooleanField(
        label=u'レジ払戻可能フラグ',
        validators=[Required()],
    )
    disapproval_reason  = TextField(
        label=u'払戻不可理由',
        validators=[Optional()],
    )
    need_stub = RadioField(
        label=u'半券要否区分',
        choices=[(u'0', u'不要'), (u'1', u'要')],
        validators=[Required()],
    )
    remarks  = TextField(
        label=u'備考',
        validators=[Optional()],
    )

def cancel_events():
    from ticketing.sej.models import SejRefundEvent
    return SejRefundEvent.all()

from wtforms.ext.sqlalchemy.fields import QuerySelectField,QuerySelectMultipleField


class SejRefundOrderForm(Form):

    event = QuerySelectField(label=u'払戻対象イベント',get_label=lambda x: u'%d:%s(%s)' % (x.id, x.title, x.sub_title), query_factory=cancel_events, allow_blank=False)
    refund_ticket_amount      = TextField(
        label=u'払戻チケット代金',
        validators=[Optional()],
    )
    refund_other_amount      = TextField(
        label=u'その他払戻金額',
        validators=[Optional()],
    )
            
class SendingMailForm(Form):
    # subject = TextField(
    #     label=u"メールタイトル",
    #     validators=[
    #         Required(),
    #     ]
    # )
    recipient = TextField(
        label=u"送り先メールアドレス",
        validators=[
            Required(),
            Email(),
        ]
    )
    bcc = TextField(
        label=u"bcc",
        validators=[
            Email(),
            Optional()
        ]
    )

class PreviewTicketSelectForm(Form):
    ticket_format_id = SelectField(
        label=u"チケットの種類", 
        choices=[], 
        validators=[Optional()],
    )
    
    item_id = HiddenField(
    )

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        ticket_formats = kwargs.get('ticket_formats')
        if ticket_formats:
            self.ticket_format_id.choices = [(t.id,  t.name) for t in ticket_formats]

class CheckedOrderTicketChoiceForm(Form):
    ticket_format_id = SelectField(
        label=u"チケット様式", 
        coerce=int, 
        choices=[], 
    )

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        ticket_formats = kwargs.get('ticket_formats')
        if ticket_formats:
            self.ticket_format_id.choices = [(t.id,  t.name) for t in ticket_formats]

