# -*- coding: utf-8 -*-
from altair.app.ticketing.core.models import SalesSegmentGroup, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod
from altair.app.ticketing.payments.api import get_payment_delivery_plugin_ids
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID
from altair.app.ticketing.events.sales_segments.forms import validate_issuing_start_at, IssuingStartAtOutTermException

class RelationValidation(object):
    def __init__(self, form):
        self.form = form
        if self.form.id.data:
            self.pdmp = PaymentDeliveryMethodPair.query.filter_by(id=form.id.data).one()
        else:
            self.sales_segment_group = SalesSegmentGroup.get(form.sales_segment_group_id.data)
            self.pdmp = merge_session_with_post(PaymentDeliveryMethodPair(), form.data)
            payment_plugin_id, delivery_plugin_id = get_payment_delivery_plugin_ids(form.payment_method_id.data,
                                                                                    form.delivery_method_id.data)
            self.pdmp.payment_method = PaymentMethod()
            self.pdmp.delivery_method = DeliveryMethod()
            self.pdmp.payment_method.payment_plugin_id = payment_plugin_id
            self.pdmp.delivery_method.delivery_plugin_id = delivery_plugin_id
            self.pdmp.payment_method.name = PaymentMethod.filter_by(id=self.form.payment_method_id.data).one().name
            self.pdmp.delivery_method.name = DeliveryMethod.filter_by(id=self.form.delivery_method_id.data).one().name

    def validate(self, status):
        status = status

        # 有効な決済方法と引取方法の組み合わせかをチェックする
        if not PaymentDeliveryMethodPair.is_valid_pair(int(self.form.payment_method_id.data),
                                                       int(self.form.delivery_method_id.data)):
            error_message = u'有効な決済方法と引取方法の組み合わせではありません'
            self.form.payment_method_id.errors.append(error_message)
            self.form.delivery_method_id.errors.append(error_message)
            status = False

        # 楽天ID決済の場合は、決済手数料と特別手数料は設定不可
        payment_method = PaymentMethod.query.filter_by(id=self.form.payment_method_id.data).first()
        if payment_method and payment_method.payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID:
            error_message = u'楽天ID決済では、決済手数料は設定できません'
            if self.form.transaction_fee.data > 0:
                self.form.transaction_fee.errors.append(error_message)
                status = False

        # コンビニ発券開始日時をチェックする
        if self.form.id.data:
            sales_segments = self.pdmp.sales_segments
        else:
            sales_segments = self.sales_segment_group.sales_segments

        for ss in sales_segments:
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
                    pdmp=self.pdmp,
                    issuing_start_day_calculation_base=self.form.issuing_start_day_calculation_base.data,
                    issuing_start_at=self.form.issuing_start_at.data,
                    issuing_interval_days=self.form.issuing_interval_days.data
                )
            except IssuingStartAtOutTermException as e:
                if self.form.issuing_start_at.data:
                    self.form.issuing_start_at.errors.append(e.message)
                else:
                    self.form.issuing_interval_days.errors.append(e.message)
                status = False
                break
        return status