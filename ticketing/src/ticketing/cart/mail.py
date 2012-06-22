# -*- coding:utf-8 -*-
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from . import logger

def on_order_completed(order_completed):
    order = order_completed.order
    request = order_completed.request
    message = create_message(order)
    mailer = get_mailer(request)
    mailer.send(message)
    logger.info("send mail to %s" % message.recipients)

def create_message(order):
    user = order.user
    user_profile = order.user.user_profile
    message = Message(
        subject=u"購入メールテスト",
        recipients=[user_profile.email],
        body=u"""購入メールテスト
======================================

購入： {order.order_no}
""".format(order=order),
        sender="ticketstar@stg2.rt.ticketstar.jp",
    )
    return message
