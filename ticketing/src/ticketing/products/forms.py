# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField, IntegerField, SelectMultipleField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional

from ticketing.products.models import PaymentMethod, DeliveryMethod

class ProductForm(Form):

    name = TextField(u'商品名',
        validators=[Required(u'入力してください')]
    )
    price = TextField(u'価格',
        validators=[Required(u'入力してください')]
    )


class PaymentDeliveryMethodPairForm(Form):

    transaction_fee = IntegerField(u'決済手数料',
        validators=[Required(u'入力してください')]
    )
    delivery_fee = IntegerField(u'配送手数料',
        validators=[Required(u'入力してください')]
    )
    discount = IntegerField(u'割引？',
        validators=[Required(u'入力してください')]
    )
    discount_unit = IntegerField(u'割引数？',
        validators=[Required(u'入力してください')]
    )
    discount_type = IntegerField(u'割引区分？',
        validators=[Required(u'入力してください')]
    )
    start_at = DateTimeField(u'販売開始日時',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M'
    )
    end_at = DateTimeField(u'販売終了日時',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M'
    )
    sales_segment_id = IntegerField(
        validators=[Required(u'入力してください')]
    )
    payment_method_id = SelectMultipleField(u'決済方法',
        validators=[Required(u'入力してください')],
        choices=[(payment_method.id, payment_method.name) for payment_method in PaymentMethod.all()]
    )
    delivery_method_id = SelectMultipleField(u'配送方法',
        validators=[Required(u'入力してください')],
        choices=[(delivery_method.id, delivery_method.name) for delivery_method in DeliveryMethod.all()]
    )
