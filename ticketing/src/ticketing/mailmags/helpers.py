# encoding: utf-8

from .models import MailSubscriptionStatus

SUBSCRIPTION_STATE_STRINGS = {
    MailSubscriptionStatus.Unsubscribed.v: u'購読解除',
    MailSubscriptionStatus.Subscribed.v: u'購読中',
    MailSubscriptionStatus.Reserved.v: u'購読中止',
    }

def subscription_status(state):
    return SUBSCRIPTION_STATE_STRINGS.get(state)
