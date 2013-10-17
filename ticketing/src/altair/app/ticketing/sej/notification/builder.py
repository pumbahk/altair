from ..helpers import create_hash_from_x_start_params, build_sej_datetime
from .models import SejNotificationType

__all__ = [
    'SejNotificationRequestParamBuilder',
    ]

class SejNotificationRequestParamBuilder(object):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def create_payment_or_cancel_request_from_record(self, n):
        return {
            'X_shori_id':           n.process_number,
            'X_shop_id':            n.shop_id,
            'X_shori_kbn':          '%02d' % int(n.payment_type),
            'X_shop_order_id':      n.order_no,
            'X_haraikomi_no':       n.billing_number or '',
            'X_hikikae_no':         n.exchange_number or '',
            'X_goukei_kingaku':     str(n.total_price),
            'X_ticket_cnt':         '%02d' % n.total_ticket_count,
            'X_ticket_hon_cnt':     '%02d' % n.ticket_count,
            'X_pay_mise_no':        n.pay_store_number,
            'pay_mise_name':        n.pay_store_name,
            'X_hakken_mise_no':     n.ticketing_store_number,
            'hakken_mise_name':     n.ticketing_store_name,
            'X_shori_time':         build_sej_datetime(n.processed_at),
            }

    def create_payment_complete_request_from_record(self, n):
        params = self.create_payment_or_cancel_request_from_record(n)
        params['X_tuchi_type'] = str(SejNotificationType.PaymentComplete.v)
        return params

    def create_cancel_request_from_record(self, n):
        params = self.create_payment_or_cancel_request_from_record(n)
        params['X_torikeshi_riyu'] = n.cancel_reason
        params['X_tuchi_type'] = '%02d' % SejNotificationType.CancelFromSVC.v
        params['X_kaishu_cnt'] = '%02d' % n.return_ticket_count
        return params

    def create_re_grant_request_from_record(self, n):
        params = {
            'X_tuchi_type':         '%02d' % SejNotificationType.ReGrant.v,
            'X_shori_id':           n.process_number,
            'X_shop_id':            n.shop_id,
            'X_shori_kbn':          '%02d' % int(n.payment_type),
            'X_shop_order_id':      n.order_no,
            'X_haraikomi_no':       n.billing_number or '',
            'X_hikikae_no':         n.exchange_number or '',
            'X_shori_kbn_new':      '%02d' % int(n.payment_type_new),
            'X_haraikomi_no_new':   n.billing_number_new or '',
            'X_hikikae_no_new':     n.exchange_number_new or '',
            'X_lmt_time_new':       build_sej_datetime(n.ticketing_due_at_new),
            'X_shori_time':         build_sej_datetime(n.processed_at),
            }
        if n.barcode_numbers is not None:
            for i in range(0, 20):
                barcode_number = n.barcode_numbers.get(i + 1)
                if barcode_number:
                    params['X_barcode_no_new_%02d' % (i + 1)] = barcode_number
        return params

    def create_expire_request_from_record(self, n):
        return {
            'X_tuchi_type':         '%02d' % SejNotificationType.TicketingExpire.v,
            'X_shori_id':           n.process_number,
            'X_shop_id':            n.shop_id,
            'X_shop_order_id':      n.order_no,
            'X_shori_kbn':          '%02d' % n.payment_type,
            'X_lmt_time':           build_sej_datetime(n.ticketing_due_at),
            'X_haraikomi_no':       n.billing_number or '',
            'X_hikikae_no':         n.exchange_number or '',
            'X_shori_time':         build_sej_datetime(n.processed_at),
            }

    processors = {
        SejNotificationType.PaymentComplete.v:
            create_payment_complete_request_from_record,
        SejNotificationType.CancelFromSVC.v:
            create_cancel_request_from_record,
        SejNotificationType.ReGrant.v:
            create_re_grant_request_from_record,
        SejNotificationType.TicketingExpire.v:
            create_expire_request_from_record,
        }

    def __call__(self, n):
        """for testing"""
        params = self.processors[int(n.notification_type)](self, n)
        params['xcode'] = create_hash_from_x_start_params(params, self.secret_key)
        return params
