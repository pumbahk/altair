# -*- coding: utf-8 -*-
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod
from altair.app.ticketing.payments.api import get_payment_delivery_plugin_ids
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID
from altair.app.ticketing.events.sales_segments.forms import validate_issuing_start_at, IssuingStartAtOutTermException

"""
決済・引取方法設定画面の項目関連チェックを行う。
1. 有効な決済方法と引取方法の組み合わせかをチェックする。
2. 楽天ペイの場合は、決済手数料と特別手数料は設定不可。
3. コンビニで引取の場合、発券開始日時をチェックする。
"""

def validate_payment_delivery_combination(status, form):
    if status:
        # 有効な決済方法と引取方法の組み合わせかをチェックする
        if not PaymentDeliveryMethodPair.is_valid_pair(int(form.payment_method_id.data),
                                                       int(form.delivery_method_id.data)):
            error_message = u'有効な決済方法と引取方法の組み合わせではありません'
            form.payment_method_id.errors.append(error_message)
            form.delivery_method_id.errors.append(error_message)
            status = False
    return status

def validate_checkout_payment_and_fees(status, form):
    if status:
        # 楽天ペイの場合は、決済手数料と特別手数料は設定不可
        payment_method = PaymentMethod.query.filter_by(id=form.payment_method_id.data).first()
        if payment_method and payment_method.payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID:
            error_message = u'楽天ペイでは、{}は設定できません'
            if form.transaction_fee.data > 0:
                form.transaction_fee.errors.append(error_message.format(u'決済手数料'))
                status = False
            if form.special_fee.data > 0:
                form.special_fee_name.errors.append(error_message.format(u'特別手数料'))
                form.special_fee.errors.append(error_message.format(u'特別手数料'))
                status = False
    return status


def validate_issuing_start_time(status, form, pdmp = None, sales_segments = None):
    if status:
        if not pdmp:
            pdmp = _build_pdmp_form_data(form)

        for ss in sales_segments:
            # パフォーマンスのみチェエクを実行する。
            if not ss.performance:
                continue
            performance_start_on = ss.performance.start_on
            performance_end_on = ss.performance.end_on or ss.performance.start_on
            ss_start_at = ss.start_at
            ss_end_at = ss.end_at
            if ss.use_default_end_at:
                ss_end_at = ss.sales_segment_group.end_for_performance(ss.performance)
            try:
                validate_issuing_start_at(
                    performance_start_on=performance_start_on,
                    performance_end_on=performance_end_on,
                    sales_segment_start_at=ss_start_at,
                    sales_segment_end_at=ss_end_at,
                    pdmp=pdmp,
                    issuing_start_day_calculation_base=form.issuing_start_day_calculation_base.data,
                    issuing_start_at=form.issuing_start_at.data,
                    issuing_interval_days=form.issuing_interval_days.data,
                    issuing_interval_time=form.issuing_interval_time.data
                )
            except IssuingStartAtOutTermException as e:
                if form.issuing_start_at.data:
                    form.issuing_start_at.errors.append(e.message)
                else:
                    form.issuing_interval_days.errors.append(e.message)
                status = False
                break
    return status

def _build_pdmp_form_data(form):
    pdmp =PaymentDeliveryMethodPair()
    payment_plugin_id, delivery_plugin_id = get_payment_delivery_plugin_ids(form.payment_method_id.data,
                                                                            form.delivery_method_id.data)
    pdmp.payment_method = PaymentMethod()
    pdmp.delivery_method = DeliveryMethod()
    pdmp.payment_method.payment_plugin_id = payment_plugin_id
    pdmp.delivery_method.delivery_plugin_id = delivery_plugin_id
    pdmp.payment_method.name = PaymentMethod.filter_by(id=form.payment_method_id.data).one().name
    pdmp.delivery_method.name = DeliveryMethod.filter_by(id=form.delivery_method_id.data).one().name
    return pdmp