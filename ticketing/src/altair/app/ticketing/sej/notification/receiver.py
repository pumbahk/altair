# encoding: utf-8

from dateutil.parser import parse as parsedate
from ..helpers import create_hash_from_x_start_params
from ..utils import JavaHashMap
from .models import SejNotificationType, SejNotification

class SejNotificationReceiverError(Exception):
    def __init__(self, params):
        self.params = params

class SejNotificationSignatureMismatch(SejNotificationReceiverError):
    pass

class SejNotificationMissingValue(SejNotificationReceiverError):
    def __init__(self, params, field_name):
        super(SejNotificationMissingValue, self).__init__(params)
        self.field_name = field_name

class SejNotificationUnknown(SejNotificationReceiverError):
    pass

class SejNotificationReceiver(object):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def populate_payment_complete(self, n, params):
        '''3-1.入金発券完了通知'''
        n.process_number        = params.get('X_shori_id')
        n.shop_id               = params.get('X_shop_id')
        n.payment_type          = str(int(params.get('X_shori_kbn')))
        n.order_no              = params.get('X_shop_order_id')
        n.billing_number        = params.get('X_haraikomi_no')
        n.exchange_number       = params.get('X_hikikae_no')
        n.total_price           = params.get('X_goukei_kingaku')
        n.total_ticket_count    = params.get('X_ticket_cnt')
        n.ticket_count          = params.get('X_ticket_hon_cnt')
        n.return_ticket_count   = params.get('X_kaishu_cnt')
        n.pay_store_number      = params.get('X_pay_mise_no')
        n.pay_store_name        = params.get('pay_mise_name')
        n.ticketing_store_number= params.get('X_hakken_mise_no')
        n.ticketing_store_name  = params.get('hakken_mise_name')
        n.cancel_reason         = params.get('X_torikeshi_riyu')
        n.processed_at          = parsedate(params.get('X_shori_time'))
        n.signature             = params.get('xcode')

    def populate_re_grant(self, n, params):
        n.process_number               = params.get('X_shori_id')
        n.shop_id                      = params.get('X_shop_id')
        n.payment_type                 = str(int(params.get('X_shori_kbn')))
        n.order_no                     = params.get('X_shop_order_id')
        n.billing_number               = params.get('X_haraikomi_no')
        n.exchange_number              = params.get('X_hikikae_no')
        n.payment_type_new             = str(int(params.get('X_shori_kbn_new')))
        n.billing_number_new           = params.get('X_haraikomi_no_new')
        n.exchange_number_new          = params.get('X_hikikae_no_new')
        n.ticketing_due_at_new         = parsedate(params.get('X_lmt_time_new'))
        n.barcode_numbers = dict()

        for idx in range(1, 20):
            barcode_number = params.get('X_barcode_no_new_%02d' % idx)
            if barcode_number:
                n.barcode_numbers[idx] = barcode_number
        n.processed_at                  = parsedate(params.get('X_shori_time'))
        n.signature                     = params.get('xcode')

    def populate_expire(self, n, params):
        n.process_number                = params.get('X_shori_id')
        n.shop_id                       = params.get('X_shop_id')
        n.order_no                      = params.get('X_shop_order_id')
        n.payment_type                  = str(int(params.get('X_shori_kbn')))
        n.ticketing_due_at              = parsedate(params.get('X_lmt_time'))
        n.billing_number                = params.get('X_haraikomi_no')
        n.exchange_number               = params.get('X_hikikae_no')
        n.processed_at                  = parsedate(params.get('X_shori_time'))
        n.signature                     = params.get('xcode')

    def unknown(self, n, params):
        raise SejNotificationUnknown(params)

    processors = {
        SejNotificationType.PaymentComplete.v   : populate_payment_complete,
        SejNotificationType.CancelFromSVC.v     : populate_payment_complete,
        SejNotificationType.ReGrant.v           : populate_re_grant,
        SejNotificationType.TicketingExpire.v   : populate_expire,
        }

    def __call__(self, params):
        hash_map = JavaHashMap()
        for k, v in params.items():
            hash_map[k] = v

        process_number = params.get('X_shori_id')
        if not process_number:
            raise SejNotificationMissingValue(params, 'X_shori_id')

        notification_type = None
        try:
            notification_type = int(params.get('X_tuchi_type'))
        except (ValueError, TypeError):
            pass

        if not notification_type:
            raise SejNotificationMissingValue(params, 'X_tuchi_type') 

        hash = create_hash_from_x_start_params(hash_map, self.secret_key)
        if hash != params.get('xcode'):
            raise SejNotificationSignatureMismatch(params)

        retry_data = False
        n = SejNotification.query.filter_by(process_number=process_number).first()
        if not n:
            n = SejNotification(notification_type=str(notification_type))
        else:
            retry_data = True

        self.processors.get(notification_type, self.__class__.unknown)(self, n, params)

        return n, retry_data
