# -*- coding:utf-8 -*-
from .plugins import (
    MULTICHECKOUT_PAYMENT_PLUGIN_ID,
    CHECKOUT_PAYMENT_PLUGIN_ID,
    SEJ_PAYMENT_PLUGIN_ID,
    RESERVE_NUMBER_PAYMENT_PLUGIN_ID,

    SHIPPING_DELIVERY_PLUGIN_ID,
    SEJ_DELIVERY_PLUGIN_ID,
    RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
    QR_DELIVERY_PLUGIN_ID,
)


def payment_status(pdmp, auth, sej):

    if pdmp.payment_method.payment_plugin_id == MULTICHECKOUT_PAYMENT_PLUGIN_ID:
        return multicheckout_auth_status(auth)
    elif pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID:
        return sej_billing_status(sej)
    else:
        return u"-"


def delivery_status(pdmp, auth, sej):
    if pdmp.payment_method.payment_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
        return sej_exchange_status(sej)
    else:
        return u"-"

def multicheckout_auth_status(auth):
    if auth is None:
        return u"-"
    elif auth.Status is None:
        return u"-"
    elif auth.Status == '100':
        return u"未オーソリ"
    elif auth.Status == '105':
        return u"オーソリ待ち"
    elif auth.Status == '110':
        return u"オーソリOK"
    elif auth.Status == '109':
        return u"オーソリNG"
    elif auth.Status == '115':
        return u"売上待ち"
    elif auth.Status == '120':
        return u"売上確定"
    elif auth.Status == '130':
        return u"売上一部取消"
    elif auth.Status == '210':
        return u"カード有効性チェックOK"
    elif auth.Status == '209':
        return u"カード有効性チェックNG"
    else:
        return u"-({auth.Status})".format(auth=auth)


def sej_billing_status(sej):
    if sej and sej.billing_number:
        return u"払込番号： {sej.billing_number}".format(sej=sej)
    else:
        return u"-"

def sej_exchange_status(sej):
    if sej and sej.exchange_number:
        return u"引換番号： {sej.exchange_number}".format(sej=sej)
    else:
        return u"-"
